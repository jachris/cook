import functools
import os
import traceback

from . import graph, misc, system


def rule(func):
    """Create a new rule. Calling it will be spawning a task.

    This function should be used as a decorator. The passed function
    must be a generator which follows the protocol.
    """
    return functools.partial(graph.spawn_task, func)


def task(func):
    return graph.spawn_task(func())


def publish(
    inputs=None, message=None, outputs=None, check=None, force=False,
    result=None, phony=False
):
    """Inform the system about the task."""
    if inputs is None:
        inputs = set()
    elif isinstance(inputs, str):
        raise TypeError(
            'Inputs is a string\n\n'
            'Rules must publish inputs in the form of an iterable. Wrap the '
            'string in a list to resolve this issue.'
        )
    else:
        inputs = set(map(os.path.abspath, inputs))
        for input in inputs:
            if not os.path.isfile(input) and not graph.has_file(input):
                raise FileNotFoundError(input)

    if not isinstance(message, str):
        if message is None:
            raise ValueError(
                'Publication did not include a message\n\n'
                'Every rule must publish a message, even phony ones.'
            )
        else:
            raise TypeError(
                'Supplied message is not a string\n\n'
                'Every rule must publish a message in form of a string. No '
                'implicit conversion is done.'
            )

    if not outputs:
        raise ValueError(
            'Rule did not declare any outputs\n\n'
            'Every rule, including phony ones, must have at least 1 output.'
        )
    elif isinstance(outputs, str):
        raise TypeError(
            'Outputs is a string\n\n'
            'Rules must publish outputs in the form of an iterable. Wrap the '
            'string in a list to resolve this issue.'
        )
    else:
        outputs = set(map(os.path.abspath, outputs))
        for output in outputs:
            if graph.has_file(output):
                raise ValueError('output collision')
            elif not phony and not misc.is_inside(output, system.build('.')):
                raise ValueError('output outside of build directory')

    if not isinstance(result, dict):
        if result is None:
            result = {}
        else:
            raise TypeError('result must be of type dict')
    elif 'outputs' in result:
        raise ValueError('outputs is reserved')
    elif 'inputs' in result:
        raise ValueError('inputs is reserved')
    result['outputs'] = outputs
    result['inputs'] = inputs
    if len(outputs) == 1 and 'output' not in result:
        [output] = outputs
        result['output'] = output

    in_files = set()
    for input in inputs:
        file = graph.get_file(input)
        if file.producer is None:
            file.stat_if_necessary()
            if not file.exists:
                raise FileNotFoundError(file.path)
        in_files.add(file)

    out_files = set()
    for output in outputs:
        if misc.is_inside(output, system.build('.')):
            file = graph.new_file(output)
            out_files.add(file)
        else:
            raise ValueError('output outside of build directory')

    if not isinstance(phony, bool):
        raise TypeError('phony must be a boolean')

    stack = traceback.extract_stack()[:-3]

    return in_files, message, out_files, check, force, result, phony, stack


def deposit(inputs=(), warnings=None):
    """Inform the system of additional inputs after execution."""
    if isinstance(inputs, str):
        raise TypeError('inputs must not be string')
    else:
        deposits = {os.path.abspath(path) for path in inputs}
        for path in deposits:
            if not os.path.isfile(path):
                raise FileNotFoundError(path)
            elif misc.is_inside(path, system.build('.')):
                raise ValueError('deposit inside build directory')
    if warnings is not None:
        warnings = warnings.strip()
    return deposits, warnings
