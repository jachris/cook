import os
import queue
import threading

from . import graph, events, record, log

defaults = set()
todo = queue.Queue()
done = queue.Queue()


# This should be rewritten, especially because task primary / secondary
# calculation is kind of misplaced here. It is by far the worst function.
def start(jobs, request=None):
    if not isinstance(jobs, int):
        raise TypeError('jobs must be of type int')
    elif jobs <= 0:
        raise ValueError('jobs must be greater than 0')
    events.on_jobs(jobs)

    # Determine requested files.
    if request is not None:
        requested = set()
        for path in map(os.path.realpath, request):
            if graph.has_file(path):
                requested.add(graph.get_file(path))
            else:
                raise ValueError('Can not find target "{}"'.format(path))
    elif defaults:
        requested = set()
        for task in defaults:
            requested.update(task.outputs)
    else:
        requested = {file for file in graph.paths.values() if file.producer}

    # All primaries must be calculated for record-cleaning and warning.
    for task in graph.tasks:
        task.calculate_primary()

    # Calculate tasks to do. Record must be loaded first.
    record.load()
    outdated = graph.all_outdated_tasks_for(requested)
    events.on_outdated(len(outdated))

    for task in graph.tasks:
        # Only display warning if we will not rebuild it.
        if record.has_primary(task) and task not in outdated:
            warnings = record.get_warnings(task)
            if warnings is not None:
                log.warning('Warnings by {}:\n{}'.format(task, warnings))

    # Skip everything if there are no outdated tasks.
    if not outdated:
        record.clean()
        record.save()
        return

    log.debug('Setup threads.')
    for identifier in range(jobs):
        Worker(identifier).start()

    added = set()
    current = 0

    for task in outdated:
        if not any(input.producer in outdated for input in task.inputs):
            added.add(task)
            todo.put(task)
            current += 1

    failed = set()
    while current:
        task, success, deposits = done.get()
        current -= 1

        outdated.remove(task)
        if not success:
            failed.add(task)
            continue

        # Put all tasks in queue that can and should be done.
        for output in task.outputs:
            for dependant in output.dependants:
                if (
                    dependant in outdated and
                    dependant not in added and
                    all(
                        input.producer not in outdated and
                        input.producer not in failed
                        for input in dependant.inputs
                    )
                ):
                    added.add(dependant)
                    todo.put(dependant)
                    current += 1

        task.deposits = {graph.get_file(deposit) for deposit in deposits[0]}
        task.warnings = deposits[1]

        if task.warnings is not None:
            log.warning('Warnings by {}:\n{}'.format(
                task.primary, task.warnings))

        task.calculate_secondary()
        record.update(task)

    record.clean()
    record.save()


def fail(task, exc):
    events.on_fail(task, exc)
    for output in task.outputs:
        if os.path.isfile(output.path):
            os.remove(output.path)
    done.put((task, False, None))


def default(*results):
    for result in results:
        if isinstance(result, graph.Result):
            defaults.add(result._task)
        else:
            raise TypeError('argument must be result')


class Worker(threading.Thread):
    def __init__(self, identifier):
        super().__init__()
        self.daemon = True
        self.identifier = identifier

    def run(self):
        while True:
            task = todo.get()
            events.on_start(self.identifier, task)
            try:
                task.prepare()
                deposits = task.execute()
                task.finalize()
            except Exception as exc:
                fail(task, exc)
            else:
                events.on_done(task)
                done.put((task, True, deposits))
