import os
import shutil

from os.path import normpath, relpath, join, abspath

build_dir = None
intermediate_dir = None
temporary_dir = None


def initialize(destination):
    global build_dir, intermediate_dir, temporary_dir

    build_dir = abspath(destination)
    cook = os.path.join(build_dir, '.cook/')
    intermediate_dir = os.path.join(cook, 'intermediate/')
    temporary_dir = os.path.join(cook, 'temporary/')

    if not os.path.isdir(destination):
        os.makedirs(destination)
    if not os.path.isdir(cook):
        os.mkdir(cook)
    if not os.path.isdir(intermediate_dir):
        os.mkdir(intermediate_dir)
    if os.path.isdir(temporary_dir):
        shutil.rmtree(temporary_dir)
    os.mkdir(temporary_dir)


def build(path_or_paths):
    if isinstance(path_or_paths, str):
        return normpath(relpath(join(build_dir, path_or_paths)))
    else:
        return {normpath(relpath(join(build_dir, path)))
                for path in path_or_paths}


def intermediate(path_or_paths):
    """..."""
    if isinstance(path_or_paths, str):
        return normpath(relpath(join(intermediate_dir, path_or_paths)))
    else:
        return {normpath(relpath(join(intermediate_dir, path)))
                for path in path_or_paths}


def temporary(path_or_paths):
    """..."""
    if isinstance(path_or_paths, str):
        return normpath(join(temporary_dir, path_or_paths))
    else:
        return {normpath(relpath(join(temporary_dir, path)))
                for path in path_or_paths}
