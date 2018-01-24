import os
import shutil
import sys

from os.path import normpath, relpath, join

from . import log, misc

build_dir = None
intermediate_dir = None
temporary_dir = None


def initialize(destination):
    global build_dir, intermediate_dir, temporary_dir

    build_dir = os.path.abspath(destination)
    cook = os.path.join(build_dir, '.cook/')
    intermediate_dir = os.path.join(cook, 'intermediate/')
    temporary_dir = os.path.join(cook, 'temporary/')

    if not os.path.isdir(build_dir):
        os.makedirs(build_dir)
    elif os.listdir(build_dir) and not os.path.isdir(cook):
        log.error(
            'The build directory "{}" is not empty and does not seem to be '
            'the location of a previous build.'.format(build_dir)
        )
        sys.exit(1)

    if not os.path.isdir(cook):
        os.mkdir(cook)
    if not os.path.isdir(intermediate_dir):
        os.mkdir(intermediate_dir)
    if os.path.isdir(temporary_dir):
        shutil.rmtree(temporary_dir)
    os.mkdir(temporary_dir)


def build(path_or_paths):
    if isinstance(path_or_paths, misc.Marked):
        return path_or_paths
    elif isinstance(path_or_paths, str):
        return misc.Marked(normpath(relpath(join(build_dir, path_or_paths))))
    else:
        return list(map(build, path_or_paths))


def intermediate(path_or_paths):
    """..."""
    if isinstance(path_or_paths, misc.Marked):
        return path_or_paths
    elif isinstance(path_or_paths, str):
        return misc.Marked(normpath(relpath(
            join(intermediate_dir, path_or_paths))))
    else:
        return list(map(intermediate, path_or_paths))


def temporary(path_or_paths):
    """..."""
    if isinstance(path_or_paths, misc.Marked):
        return path_or_paths
    elif isinstance(path_or_paths, str):
        return misc.Marked(normpath(join(temporary_dir, path_or_paths)))
    else:
        return list(map(temporary, path_or_paths))
