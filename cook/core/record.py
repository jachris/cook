import json
import os

from .system import build, log

data = None


def load():
    """Load serialized data if a record-file exists."""
    global data

    record = build('.cook/record.json')
    if os.path.isfile(record):
        with open(record) as file:
            data = json.load(file)
    else:
        data = {}


def save():
    """Write the serialized data to the predefined location."""
    with open(build('.cook/record.json'), 'w') as file:
        json.dump(data, file)


def clean():
    from . import graph  # TODO: make it better

    current_primaries = {task.primary for task in graph.tasks}

    for primary in list(data.keys()):
        if primary not in current_primaries:
            del data[primary]

    record = os.path.abspath(build('.cook/record.json'))
    temporary = build('.cook/temporary/')

    # Build-directory cleaning should not really happen here.
    for root, directories, files in os.walk(build('.')):
        root = os.path.normpath(root)
        if root.startswith(temporary):
            continue
        for file in files:
            path = os.path.abspath(os.path.join(root, file))
            if not path == record and not graph.has_file(path):
                log.warning('Removing non-declared file: ' + path)
                os.remove(path)


def has_primary(primary):
    """Return true if the last run had a rule with that primary."""
    return primary in data


def match_secondary(primary, secondary):
    return data[primary][0] == secondary


def get_deposits(primary):
    return data[primary][1]


def get_warnings(primary):
    return data[primary][2]


def update(task):
    deposits = [file.path for file in task.deposits]
    data[task.primary] = [task.secondary, deposits, task.warnings]
