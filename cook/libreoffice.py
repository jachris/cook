import os

from . import core

_soffice = core.which('soffice')


@core.rule
def convert(source, destination=None, format=None):
    if _soffice is None:
        raise FileNotFoundError('libreoffice (soffice) was not found')

    source = core.source(source)

    if format is None and destination is None:
        raise ValueError

    if destination is None:
        name = core.checksum(source, format) + '.' + format
        destination = core.intermediate(name)
    else:
        destination = core.build(destination)
        if format is None:
            format = core.extension(destination)

    in_base, in_ext = os.path.splitext(os.path.basename(source))
    in_ext = in_ext[1:]

    yield core.publish(
        inputs=[source, _soffice],
        outputs=[destination],
        message='Convert {} to "{}"'.format(in_ext.upper(), destination),
        result={
            'output': core.absolute(destination),
        },
    )

    out_dir = core.temporary(core.random())
    os.mkdir(out_dir)
    command = [_soffice, '--headless', '--convert-to', format,
               '--outdir', out_dir, source]
    core.call(command)
    out_path = os.path.join(out_dir, in_base + '.' + format)
    os.rename(out_path, destination)
