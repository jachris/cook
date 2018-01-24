import os

from . import core

_pdflatex = core.which('pdflatex')


@core.rule
def document(
    source, name=None, contains=None, texinputs=None, scan=True
):
    if name is None:
        name = core.base_no_ext(source) + '.pdf'
    name = core.build(name)

    if contains is None:
        contains = []

    source = core.resolve(source)

    inputs = [source]
    inputs.extend(contains)

    yield core.publish(
        inputs=inputs + [_pdflatex],
        outputs=[name],
        message='Compile LaTeX to "{}"'.format(name)
    )

    env = {}

    if texinputs is not None:
        texinputs = core.resolve(texinputs)
        env['TEXINPUTS'] = '.:{}::'.format(os.pathsep.join(
            texinput for texinput in texinputs)
        )

    aux_dir = core.temporary(core.random())
    os.mkdir(aux_dir)

    cmd = [_pdflatex, '-output-directory', aux_dir, '-jobname', 'document']
    if scan:
        cmd.append('-recorder')
    cmd.append(source)

    # How many times should this be done? Sometimes one is enough, sometimes
    # two or even more. It seems it is possible to determine it - this is very
    # important to avoid unnecessary rebuilds.
    core.call(cmd, env=env)
    core.call(cmd, env=env)

    pdf = os.path.join(aux_dir, 'document.pdf')
    os.rename(pdf, name)

    if scan:
        record = os.path.join(aux_dir, 'document.fls')
        used = {os.path.realpath(input) for input in inputs}

        dependencies = set()
        with open(record) as stream:
            for line in stream:
                line = line.strip()
                if line.startswith('INPUT'):
                    path = line[6:]
                    if not (path.startswith('/usr/') or path.startswith('/etc/') or
                            path.startswith('/var/')):
                        path = os.path.realpath(path)
                        if path not in used and not path.startswith(aux_dir):
                            dependencies.add(path)
        dependencies.difference_update(contains)
        yield core.deposit(x for x in dependencies if not x.endswith('.aux'))
