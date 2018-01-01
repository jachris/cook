import glob as _glob
import hashlib
import os
import platform
import random as _random
import struct
import subprocess
import sys
import threading

from . import loader, log

system = platform.system()
linux = system == 'Linux'
windows = system == 'Windows'
mac = system == 'darwin'


def cache(func):
    """Thread-safe caching."""
    lock = threading.Lock()
    results = {}

    def wrapper(*args, **kwargs):
        identifier = checksum(args, kwargs)
        if identifier in results:
            return results[identifier]
        with lock:
            if identifier in results:
                return results[identifier]
            result = func(*args, **kwargs)
            results[identifier] = result
            return result

    return wrapper


def checksum(*objects):
    """Calculate an MD5-checksum (128 bits) of the given object.

    The types of the object and it's elements (in case of a container)
    may only consist of:
    - int
    - None
    - bool
    - str
    - bytes, bytearray, ...
    - dict, ...
    - set, frozenset, ...
    - list, tuple, generator, ...

    A TypeError will be raised if an unsupported type is encountered.

    Please note that cyclic containers lead to an exceeding of the
    maximum recursion depth, which raises to a RuntimeError.

    The builtin hash-function cannot be used, since it is randomized
    for strings, bytes and datetime objects and sometimes even slower
    when trying to get a byte representation.
    """
    hasher = hashlib.md5()
    _checksum(hasher, objects)
    return hasher.hexdigest()


def _checksum(hasher, obj):
    if isinstance(obj, str):
        hasher.update(b'\x00' + obj.encode())
    elif isinstance(obj, bool):
        hasher.update(b'\x01' if obj else b'\x02')
    elif isinstance(obj, int):
        if obj >= 0:
            hasher.update(b'\x03')
        else:
            hasher.update(b'\x04')
            obj *= -1
        while obj > 255:
            hasher.update(bytes([obj % 256]))
            obj >>= 8
        hasher.update(bytes([obj]))
    elif isinstance(obj, float):
        hasher.update(b'\x05')
        hasher.update(struct.pack('d', obj))
    elif obj is None:
        hasher.update(b'\x06')
    elif isinstance(obj, bytes) or isinstance(obj, bytearray):
        hasher.update(b'\x07')
        hasher.update(obj)
    elif isinstance(obj, dict):
        hasher.update(b'\x08')
        _checksum(hasher, sorted(obj.items()))
    elif isinstance(obj, set) or isinstance(obj, frozenset):
        hasher.update(b'\x09')
        _checksum(hasher, sorted(obj))
    elif isinstance(obj, list) or isinstance(obj, tuple):
        hasher.update(b'\x0a')
        for element in obj:
            hasher.update(b'\x0b')
            _checksum(hasher, element)
    else:
        raise TypeError('Unsupported object type "{}".'.format(type(obj)))


def which(file, env=os.environ):
    """Tries to find the exact path for a given filename.

    Returns None if no file was found.
    """
    if file is None:
        return None
    for path in env.get('PATH', '').split(os.pathsep):
        if path:
            result = os.path.join(path, file)
            if os.path.exists(result):
                return os.path.realpath(result)
    return None


if sys.version_info >= (3, 5):
    def glob(pathname):
        return absolute(filter(os.path.isfile, _glob.iglob(
            loader.source(pathname), recursive=True)))
else:
    def glob(pathname):
        return absolute(filter(os.path.isfile, _iglob(
            loader.source(pathname))))

    def _iglob(pathname):
        """Return an iterator which yields the paths matching a pathname pattern.

        The pattern may contain simple shell-style wildcards a la
        fnmatch. However, unlike fnmatch, filenames starting with a
        dot are special cases that are not matched by '*' and '?'
        patterns.

        If recursive is true, the pattern '**' will match any files and
        zero or more directories and subdirectories.

        Note: The recursive glob was introduced in Python 3.5. This is more
        or less a straight back-port in order to support older versions.
        """
        dirname, basename = os.path.split(pathname)
        if not _glob.has_magic(pathname):
            if basename:
                if os.path.lexists(pathname):
                    yield pathname
                else:
                    raise FileNotFoundError
            else:
                if os.path.isdir(dirname):
                    yield pathname
                else:
                    raise NotADirectoryError
            return
        if not dirname:
            if basename == '**':
                for name in _glob2(dirname, basename):
                    yield name
            else:
                for name in _glob.glob1(dirname, basename):
                    yield name
            return
        if dirname != pathname and _glob.has_magic(dirname):
            dirs = _iglob(dirname)
        else:
            dirs = [dirname]
        if _glob.has_magic(basename):
            if basename == '**':
                glob_in_dir = _glob2
            else:
                glob_in_dir = _glob.glob1
        else:
            glob_in_dir = _glob.glob0(dirname, basename)
        for dirname in dirs:
            for name in glob_in_dir(dirname, basename):
                yield os.path.join(dirname, name)


    def _glob2(dirname, pattern):
        if dirname:
            yield pattern[:0]
        for name in _rlistdir(dirname):
            yield name


    def _rlistdir(dirname):
        if not dirname:
            dirname = os.curdir
        try:
            names = os.listdir(dirname)
        except os.error:
            return
        for x in names:
            if not _glob._ishidden(x):
                yield x
                path = os.path.join(dirname, x) if dirname else x
                for y in _rlistdir(path):
                    yield os.path.join(x, y)


def absolute(path_or_paths):
    """..."""
    if path_or_paths is None:
        return None
    elif isinstance(path_or_paths, str):
        return os.path.abspath(path_or_paths)
    else:
        return list(map(os.path.abspath, path_or_paths))


def relative(path_or_paths):
    """..."""
    if path_or_paths is None:
        return None
    elif isinstance(path_or_paths, str):
        return os.path.normpath(os.path.relpath(path_or_paths))
    else:
        return list(map(os.path.normpath, map(os.path.relpath, path_or_paths)))


def random(suffix=''):
    return ''.join(_random.choice('abcdefghijklmnopqrstuvwxyz1234567890')
                   for _ in range(16)) + suffix


def extension(path):
    return os.path.splitext(os.path.basename(path))[1][1:]


# TODO: Change name or remove / alternative.
def base_no_ext(path):
    return os.path.splitext(os.path.basename(path))[0]


def is_inside(path, directory):
    path = os.path.normpath(os.path.abspath(path)).split(os.sep)
    directory = os.path.normpath(os.path.abspath(directory)).split(os.sep)

    for n, component in enumerate(directory):
        if path[n] != component:
            return False
    return True


class CallError(Exception):
    def __init__(self, returned, command, output=None):
        self.returned = returned
        self.command = command
        self.scommand = subprocess.list2cmdline(command)
        self.output = output

    def __str__(self):
        cmdline = subprocess.list2cmdline(self.command)
        return 'Command "{}" returned {}'.format(
            cmdline, self.returned)


def call(command, cwd=None, env=None, timeout=None):
    log.debug('CALL {}'.format(subprocess.list2cmdline(command)))

    if env is None:
        env = os.environ

    try:
        if windows:
            output = subprocess.check_output(
                command, stderr=subprocess.STDOUT, env=env, cwd=cwd,
                stdin=subprocess.DEVNULL, timeout=timeout,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            output = subprocess.check_output(
                command, stderr=subprocess.STDOUT, env=env, cwd=cwd,
                stdin=subprocess.DEVNULL, timeout=timeout,
                preexec_fn=os.setpgrp
            )
        return output.decode(errors='ignore')
    except subprocess.CalledProcessError as e:
        output = e.output.decode(errors='ignore')
        raise CallError(e.returncode, e.cmd, output) from None
