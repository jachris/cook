from . import events


def debug(*objects, sep=' '):
    events.on_debug(sep.join(map(str, objects)))


def info(*objects, sep=' '):
    events.on_info(sep.join(map(str, objects)))


def warning(*objects, sep=' '):
    events.on_warning(sep.join(map(str, objects)))


def error(*objects, sep=' '):
    events.on_error(sep.join(map(str, objects)))
