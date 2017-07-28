import os
import stat
import types

from . import misc, record

paths = {}
stats = 0
tasks = set()


class File:
    def __init__(self, path):
        self.path = path
        self.producer = None
        self.dependants = set()
        self.timestamp = None
        self.exists = None
        self.phony = False

    def changed(self):
        return self.timestamp != os.path.getmtime(self.path)

    def __repr__(self):
        return '<Produced File>' if self.producer else '<File>'

    def stat(self):
        global stats
        stats += 1
        try:
            st = os.stat(self.path)
        except OSError:
            self.exists = False
            self.timestamp = None
        else:
            if stat.S_ISREG(st.st_mode):
                self.exists = True
                self.timestamp = st.st_mtime
            else:
                self.exists = False
                self.timestamp = None

    def stat_if_necessary(self):
        if self.exists is None:
            return self.stat()
        return False


class Task:
    def __init__(self, generator, message, check, force, phony, stack):
        self.generator = generator
        self.message = message
        self.check = check
        self.force = force
        self.phony = phony
        self.result = None

        self.inputs = set()
        self.outputs = set()
        self.primary = None
        self.secondary = None
        self.deposits = set()
        self.warnings = None
        self.stack = stack

    def prepare(self):
        if not self.phony:
            for output in self.outputs:
                dirname = os.path.dirname(output.path)
                if dirname and not os.path.isdir(dirname):
                    os.makedirs(dirname, exist_ok=True)
        for input in self.inputs:
            if not input.producer and input.changed():
                raise RuntimeError(
                    'Input file \'{}\' was changed before execution\n\n'
                    'Input timestamps are required to stay constant '
                    'throughout the execution of the build.'
                    .format(input.path)
                )

    def execute(self):
        try:
            deposits = next(self.generator)
        except StopIteration:
            deposits = set(), None
        else:
            try:
                next(self.generator)
            except StopIteration:
                pass
            else:
                raise RuntimeError(
                    'Task is not exhausted after second yield\n\n'
                    'It is required that the generator yields at most two '
                    'time - once for the publication, once for the '
                    'deposit. Then it must be done.'
                )
        self.generator = None
        return deposits

    def finalize(self):
        for input in self.inputs:
            if not input.producer and input.changed():
                raise RuntimeError(
                    'Input file \'{}\' was changed while building.\n\n'
                    'Input files must remain unchanged during the build '
                    'process. This is to ensure correct outputs.'
                    .format(input.path)
                )

        if not self.phony:
            for output in self.outputs:
                previous = output.timestamp
                output.stat()
                if not output.exists:
                    raise RuntimeError(
                        'Task did not create output \'{}\'\n\n'
                        'All outputs must exist after the task is run. '
                        'Maybe the outputs are not specified correctly.'
                        .format(output.path)
                    )
                if output.timestamp == previous:
                    raise RuntimeError(
                        'Output file \'{}\' was not touched by task\n\n'
                        'Every rule must make sure that the output '
                        'timestamps are updated whenever it is executed.'
                        .format(output.path)
                    )

    def calculate_primary(self):
        # input paths, output paths, check
        inputs = {file.path for file in self.inputs}
        outputs = {file.path for file in self.outputs}

        timestamps = set()
        for file in self.inputs:
            if file.producer is None:
                file.stat_if_necessary()
                timestamps.add(file.timestamp)

        self.primary = misc.checksum(inputs, timestamps, outputs, self.check)

    def calculate_secondary(self):
        # Lookup output timestamps for the checksum.
        out_times = set()
        for file in self.outputs:
            file.stat_if_necessary()
            if file.exists:
                out_times.add(file.timestamp)
            else:
                out_times.add(-1)

        # Also lookup deposit timestamps for checksum.
        if record.has_primary(self.primary):
            self.deposits = [get_file(path) for path in
                             record.get_deposits(self.primary)]
        deposit_times = set()
        for file in self.deposits:
            file.stat_if_necessary()
            if file.exists:
                deposit_times.add(os.path.getmtime(file.path))
            else:
                deposit_times.add(-1)

        # Save the new checksum and deposits to the record file.
        self.secondary = misc.checksum(out_times, deposit_times)

    def is_dirty(self):
        if self.force:
            return True
        elif not record.has_primary(self.primary):
            return True
        elif not self.phony and not all(os.path.isfile(file.path)
                                        for file in self.outputs):
            return True
        else:
            self.calculate_secondary()
            if not record.match_secondary(self.primary, self.secondary):
                return True
            else:
                return False


def all_parent_tasks(tasks):
    stack = list(tasks)
    parents = set(stack)

    for task in stack:
        for file in task.inputs:
            producer = file.producer
            if producer is not None and producer not in parents:
                stack.append(producer)
                parents.add(producer)
    return parents


def all_outdated_tasks_for(files):
    parents = all_parent_tasks(file.producer for file in files)

    # log.debug('Calculating secondary')
    # for task in parents:
    #     task.calculate_secondary()

    # log.debug('Calculating dirtyness')
    stack = [task for task in parents if task.is_dirty()]

    # log.debug('Propagating dirtyness')
    outdated = set(stack)
    while stack:
        task = stack.pop()
        for output in task.outputs:
            for dependant in output.dependants:
                if dependant not in outdated and dependant in parents:
                    outdated.add(dependant)
                    stack.append(dependant)
    return outdated


def spawn_task(func, *args, **kwargs):
    generator = func(*args, **kwargs)

    if not isinstance(generator, types.GeneratorType):
        raise RuntimeError(
            'Could not iterate on the rule object\n\n'
            'An invoked rule turned out to not be iterable. Every rule must '
            'follow the corresponding protocol, which dictates that rules '
            'must yield a publication and therefore be a generator. This '
            'error was caused by an incomplete rule definition and not by the '
            'calling context. Maybe \'yield\' in front of core.publish() is '
            'missing.'
        )
    try:
        publication = next(generator)
    except StopIteration:
        raise RuntimeError(
            'Rule did not yield anything after invocation\n\n'
            'Every rule must yield a publication according to the rule '
            'protocol. The rule seems to be an iterable, but it did not yield '
            'anything. This was most-likely caused by incomplete if/elif '
            'branching of the rule defintion and not by the calling context.'
        ) from None

    if not isinstance(publication, tuple) or not len(publication) == 8:
        raise ValueError(
            'Rule did yield something, but not a publication\n\n'
            'Every rule must first yield the result of a core.publish() call. '
            'This is an error within the definition of the rule, not the '
            'calling context.'
        )

    inputs, message, outputs, check, force, result, phony, stack = publication
    task = Task(generator, message, check, force, phony, stack)

    for input in inputs:
        task.inputs.add(input)
        input.dependants.add(task)

    for output in outputs:
        task.outputs.add(output)
        output.producer = task

    task.result = Result(**result)
    task.result._task = task

    tasks.add(task)

    # task.calculate_primary()
    #
    # if record.match_primary(task.primary):
    #     for deposit in record.get_deposits(task.primary):
    #         file = get_file(deposit)
    #         task.deposits.add(file)
    #         file.dependants.add(task)
    # primaries.add(task.primary)

    return task.result


def try_file(path):
    """Return the corresponding file if found."""
    if path in paths:
        return paths[path]
    else:
        return None


def has_file(path):
    """Return True if the file is registered."""
    return path in paths


def get_file(path):
    """Create a new file if it does not exist before."""
    if path in paths:
        return paths[path]
    else:
        file = File(path)
        paths[path] = file
        return file


def new_file(path):
    """Create a new file, that must not exist before."""
    if path not in paths:
        file = File(path)
        paths[path] = file
        return file
    else:
        raise ValueError('File already exists: {}'.format(path))


class Result:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return 'Result({})'.format(', '.join(
            '{}={}'.format(name, repr(value)) for name, value in
            sorted(self.__dict__.items()) if not name.startswith('_')))

    def __dir__(self):
        return [attr for attr in self.__dict__ if not attr.startswith('_')]
