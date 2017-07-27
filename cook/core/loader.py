"""Management of scripts and their directories.

Any build script can make use of this module by loading other scripts,
allowing the existence of hierarchy and separation of concerns. Paths
may be interpreted relatively to the script that is being executed.
"""

from os.path import normpath, relpath, join, abspath, isdir, isfile, dirname

from . import events

loaded = {}
executing = set()
directories = ['.']


def resolve(path_or_paths):
    """Interpret given paths relative to the current script directory.

    If 'path_or_paths' is a single string, the resolved path is
    returned as a string as well. Otherwise, it is interpreted as an
    iterable and a set is returned.

    Absolute paths will be returned as they are.
    """
    if isinstance(path_or_paths, str):
        return normpath(relpath(join(directories[-1], path_or_paths)))
    else:
        return [normpath(relpath(join(directories[-1], path)))
                for path in path_or_paths]


def load(path):
    """Run the given script and return its symbols.

    The path of the script is interpreted relatively to the current
    script directory. If it points to an directory, then it will be
    assumed that the script to load is a file named 'cook.py'.

    Loading the same script multiple times will not execute it more
    than once - instead the last result will be returned.

    A RuntimeError will be raised if a cycle is detected.
    """
    path = abspath(resolve(path))
    if isdir(path):
        directory = path
        path = join(directory, 'BUILD.py')
    else:
        directory = dirname(path)

    if path in executing:
        raise RuntimeError('detected cyclic dependency at "{}"'.format(path))
    if path in loaded:
        return loaded[path]
    if not isfile(path):
        raise FileNotFoundError(path)

    events.on_load(path)
    directories.append(directory)
    executing.add(path)

    with open(path) as f:
        content = f.read()
    symbols = {}
    exec(compile(content, path, 'exec'), symbols)

    directories.pop()
    executing.remove(path)
    events.on_loaded(path)

    namespace = Script(path, symbols)
    loaded[path] = namespace
    return namespace


class Script:
    def __init__(self, path, symbols):
        self.__path = path
        for key, value in symbols.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<symbols from "{}">'.format(self.__path)

    def __dir__(self):
        return [attr for attr in self.__dict__
                if not attr.startswith('__') and attr is not '_Script__path']
