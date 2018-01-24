from cook import core


@core.rule
def run(
    command, outputs, inputs=None, message=None, env=None, timeout=None,
    cwd=None
):
    inputs = core.resolve(inputs or [])
    outputs = core.build(outputs)
    command[0] = core.which(command[0])

    yield core.publish(
        inputs=inputs + [command[0]],
        outputs=outputs,
        message=message or 'Running "{}"'.format(command[0]),
        check=[env, command]
    )

    real = []
    for token in command:
        if token == '$INPUTS':
            real.extend(inputs)
        elif token == '$OUTPUTS':
            real.extend(outputs)
        else:
            real.append(token)
    core.call(real, env=env, timeout=timeout, cwd=cwd)
