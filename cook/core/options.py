import builtins

from . import log, events

TRUE_STRINGS = frozenset(('yes', 'y', 'on', 'true', '1'))
FALSE_STRINGS = frozenset(('no', 'n', 'off', 'false', '0'))

requested = set()


def option(name, type=bool, default=None, help=''):
    """Allowed types: str, int, bool, float."""
    if type not in (str, int, bool, float):
        raise ValueError(
            'Cannot declare option of type "{}"\n\n'
            'The only valid values for the \'type\' parameter are str, int, '
            'float and bool. If you need another type (e.g. list), then you '
            'should request a string and convert it explicitly.'
            .format(type)
        )

    if default is None:
        default = type()
    elif not isinstance(default, type):
        raise TypeError(
            'Mismatching default value and type\n\n'
            'The specified default value of type "{}" does not correspond to '
            'the given type "{}". Default values must have the same types.'
            .format(builtins.type(default), type)
        )

    name = name.upper()
    if name in requested:
        raise ValueError(
            'Option "{}" was declared twice\n\n'
            'All options can be only declared once. This ensures that there '
            'are no conflicting definitions. You can resolve this issue by '
            'creating a shared file which declares this option and '
            'core.load() it.'
            .format(name)
        )

    requested.add(name)
    result = None

    value = events.on_option(name, type, default, help)
    given_type = builtins.type(value)
    if given_type is type:
        result = value
    elif not isinstance(value, str):
        raise TypeError('need {} or str, not {}'.format(type, given_type))
    elif type is int:
        try:
            result = int(value)
        except ValueError:
            raise TypeError(
                'Could not convert "{}" to an integer\n\n'
                'Integer values are only accepted as sequences of digits.'
                .format(value)
            ) from None
    elif type is bool:
        value = value.lower()
        if value in TRUE_STRINGS:
            result = True
        elif value in FALSE_STRINGS:
            result = False
        else:
            raise ValueError(
                'Invalid value for option "{}" of type bool\n\n'
                'You must supply one of these values: "yes", "y", "on", "true"'
                ' and "1" or "no", "n", "off", "false" and "0". The value is '
                'not case-sensitive.'
                .format(name)
            )
    elif type is float:
        try:
            result = float(value)
        except ValueError:
            raise TypeError(
                'Could not convert "{}" to a float\n\n'
                'The decimal point character must be "." and an exponent '
                'suffix may be given by an case-insensitive e followed by'
                'a whole number.'
                .format(value)
            ) from None

    log.debug('Evaluated option {} as {}.'.format(name, repr(result)))
    return result
