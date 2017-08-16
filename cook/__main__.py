import argparse
import os
import platform
import sys
import traceback
import threading

from .core import system, loader, events, builder
from .core.misc import is_inside, relative

windows = platform.system() == 'Windows'
lock = threading.Lock()

if windows:
    import ctypes
    import functools
    stdout_id = ctypes.c_ulong(0xfffffff5)
    ctypes.windll.Kernel32.GetStdHandle.restype = ctypes.c_ulong
    stdout_handle = ctypes.windll.Kernel32.GetStdHandle(stdout_id)
    set_color = functools.partial(
        ctypes.windll.Kernel32.SetConsoleTextAttribute, stdout_handle)

    def print_progress(percent, text):
        with lock:
            print('[', end='', flush=True)
            set_color(10)
            print('{:>3}%'.format(percent), end='', flush=True)
            set_color(7)
            print(']', text)

    def on_debug(msg):
        if verbose:
            with lock:
                print('[', end='', flush=True)
                set_color(11)
                print('DEBUG', end='', flush=True)
                set_color(7)
                print(']', msg)

    def on_info(msg):
        with lock:
            print('[', end='', flush=True)
            set_color(10)
            print('INFO', end='', flush=True)
            set_color(7)
            print(']', msg)

    def on_warning(msg):
        with lock:
            print('[', end='', flush=True)
            set_color(14)
            print('WARNING', end='', flush=True)
            set_color(7)
            print(']', msg)

    def on_error(msg):
        with lock:
            print('[', end='', flush=True)
            set_color(12)
            print('ERROR', end='', flush=True)
            set_color(7)
            print(']', msg)
else:
    def print_progress(percent, text):
        print('[\033[32m{:>3}%\033[0m]'.format(percent), text)

    def on_debug(msg):
        if verbose:
            print('[\033[34mDEBUG\033[0m]', msg)

    def on_info(msg):
        print('[\033[32mINFO\033[0m]', msg)

    def on_warning(msg):
        print('[\033[33mWARNING\033[0m]', msg)

    def on_error(msg):
        print('[\033[31mERROR\033[0m]', msg)

given = {}
options = {}
started = 0
outdated = 0
failed = 0
verbose = False


def good_path(path):
    if is_inside(path, '.'):
        return relative(path)
    else:
        return path


def on_option(name, type, default, help):
    options[name] = (type, default, help)
    if name in given:
        return given[name]
    else:
        return default


def on_fail(task, exc):
    global failed
    failed += 1

    on_error('Failed task: {}'.format(', '.join(
        good_path(file.path) for file in task.outputs)))

    if verbose:
        print('Saved traceback (most recent call last):')
        tb = remove_traceback_noise(task.stack)
        print(''.join(traceback.format_list(tb)))

    if hasattr(exc, 'command'):
        if verbose:
            tb = traceback.extract_tb(exc.__traceback__)
            tb = remove_traceback_noise(tb)
            print('Traceback (most recent call last):')
            print(''.join(traceback.format_list(tb)), end='')
            print(''.join(traceback.format_exception_only(type(exc), exc)))
            print('$', exc.scommand)
        print(exc.output, end='')
    else:
        tb = traceback.extract_tb(exc.__traceback__)
        tb = remove_traceback_noise(tb)
        print('Traceback (most recent call last):')
        print(''.join(traceback.format_list(tb)), end='')
        print(''.join(traceback.format_exception_only(type(exc), exc)), end='')


def on_start(job, task):
    global started
    percent = int(100 * started / outdated)
    started += 1
    print_progress(percent, task.message)


def on_outdated(count):
    global outdated
    outdated = count


def main():
    global verbose

    parser = argparse.ArgumentParser(
        usage='%(prog)s <args> [target] [option=value] ...',
        formatter_class=HelpFormatter,
        add_help=False
    )
    parser._optionals.title = 'Arguments'

    if hasattr(os, 'cpu_count'):
        jobs = round(1.5 * (os.cpu_count() or 4)) + 1
    else:
        jobs = 6

    arg = parser.add_argument
    arg('-h', '--help', action='help', help='Show this help message and exit')
    arg('-b', '--build', metavar='PATH', default='.',
        help='Location of BUILD.py')
    arg('-j', '--jobs', type=int, metavar='INT',
        help='Number of jobs (default: {})'.format(
            jobs))
    arg('-v', '--verbose', action='store_true', help='Enable debug mode')
    arg('-o', '--output', metavar='PATH',
        help='Override build directory')
    arg('rest', nargs='*', help=argparse.SUPPRESS)
    arg('--options', action='store_true', help='List all options and exit')
    arg('--targets', action='store_true', help='List all targets and exit')
    arg('--results', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()

    verbose = args.verbose
    events.on_debug = on_debug
    events.on_info = on_info
    events.on_warning = on_warning
    events.on_error = on_error
    events.on_option = on_option
    events.on_start = on_start
    events.on_fail = on_fail
    events.on_outdated = on_outdated

    request = set()
    for entry in args.rest:
        if '=' in entry:
            key, value = entry.split('=', 1)
            given[key.upper()] = value
        else:
            request.add(entry)

    if os.path.isfile(args.build):
        build = args.build
    else:
        build = os.path.join(args.build, 'BUILD.py')
        if not os.path.isfile(build):
            on_error('Could not find BUILD.py at {}'.format(
                os.path.abspath(args.build)))
            return 1

    if args.output is None:
        output = os.path.join(os.path.dirname(build), 'build/')
    else:
        output = args.output

    system.initialize(output)
    try:
        loader.load(build)
    except Exception as exc:
        on_error('Failed to load BUILD.py - see below')
        tb = traceback.extract_tb(exc.__traceback__)[2:]
        tb = remove_traceback_noise(tb)
        print('Traceback (most recent call last):')
        print(''.join(traceback.format_list(tb)), end='')
        print(''.join(traceback.format_exception_only(type(exc), exc)), end='')
        return 2

    remaining = {x.lower() for x in given} - {x.lower() for x in options}
    if remaining:
        raise ValueError('Invalid options - ' + ', '.join(remaining))

    if args.options:
        print('{:<10} {:<5} {:<10} {:<20}'.format(
            'name', 'type', 'default', 'help'))
        print('-'*50)
        for name in options:
            tp, default, help = options[name]
            print('{:<10} {:<5} {:<10} {:<20}'.format(
                name.lower(), tp.__name__, str(default), help))
        return

    if args.targets:
        from .core import graph
        ignore = os.sep + '.cook' + os.sep
        targets = []
        for task in graph.tasks:
            for output in task.outputs:
                if ignore not in output.path:
                    targets.append(os.path.relpath(output.path))
        targets.sort()
        for target in targets:
            print(target)
        return

    if args.results:
        # This is currently very hacky. Writing a json file is probably not
        # needed. The IDE tool could just drive the system directly.
        import json
        from .core import graph

        results = {}
        for task in graph.tasks:
            task.calculate_primary()
            results[task.primary] = task.result.__dict__

        def set_to_list(s):
            if isinstance(s, set):
                return list(s)
            else:
                return None

        with open('results.json', 'w') as file:
            json.dump(results, file, default=set_to_list)
        return

    builder.start(args.jobs or jobs, request or None)

    if not outdated:
        on_info('No work to do.')
    elif not failed:
        print_progress(100, 'Done.')
    else:
        on_warning('Failed tasks: {}'.format(failed))
        return 1


def remove_traceback_noise(tb):
    forbidden = (
        ('/core/loader.py', 'load', 'exec('),
        ('/core/graph.py', 'spawn_task', 'next('),
        ('/core/builder.py', 'run', '.execute('),
        ('/core/graph.py', 'execute', 'next('),
        ('', '<module>', 'load_entry_point('),
        ('/cook/__main__.py', 'main', 'load('),
        ('/core/misc.py', 'call', 'raise')
    )

    return [entry for entry in tb if not any(
        entry[0].endswith(data[0]) and
        entry[2] == data[1] and
        data[2] in entry[3]
        for data in forbidden
    )]


class HelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            return metavar
        else:
            parts = []
            if action.nargs == 0:
                parts.extend(action.option_strings)
            else:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                parts.extend(action.option_strings)
                parts[-1] += ' ' + args_string
            return ', '.join(parts)

    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = 'Usage: '
        return super()._format_usage(usage, actions, groups, prefix)


if __name__ == '__main__':
    # TODO: Exit gracefully?
    sys.exit(main() or 0)
