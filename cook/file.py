import hashlib
from urllib.request import urlopen

from . import core


@core.rule
def copy(input, output):
    input = core.source(input)
    output = core.build(output)

    yield core.publish(
        inputs=[input],
        outputs=[output],
        message='Copy {} to {}'.format(input, output),
    )

    with open(input, 'rb') as infile:
        with open(output, 'wb') as outfile:
            outfile.write(infile.read())


@core.rule
def template(
    source, mapping, destination=None, left='###', right='###'
):
    source = core.source(source)

    if destination is None:
        name = core.checksum(source, mapping, left, right)
        name += '.' + core.extension(source)
        destination = core.intermediate(name)
    else:
        destination = core.build(destination)

    yield core.publish(
        inputs=[source],
        outputs=[destination],
        message='Evaluate template "{}"'.format(source),
        check=[mapping, left, right]
    )

    with open(source, 'r') as infile:
        content = infile.read()
    for key, value in mapping.items():
        key = left + key + right
        if key in content:
            content = content.replace(key, value)
        else:
            raise ValueError('key "{}" not in content'.format(key))
    with open(destination, 'w') as outfile:
        outfile.write(content)


@core.rule
def group(inputs, name):
    name = core.build(name)

    yield core.publish(
        inputs=inputs,
        message='Group "{}" done.'.format(name),
        outputs=[name],
        phony=True
    )


@core.rule
def download(url, destination, sha256):
    destination = core.build(destination)

    yield core.publish(
        message='Downloading "{}"'.format(url),
        outputs=[destination],
        check=[url, sha256]
    )

    hasher = hashlib.sha256()
    with open(destination, 'wb') as stream:
        with urlopen(url) as remote:
            data = remote.read(4096)
            while data:
                hasher.update(data)
                stream.write(data)
                data = remote.read(4096)

    checksum = hasher.hexdigest()
    if checksum != sha256:
        raise ValueError('Expected {}, got {}'.format(sha256, checksum))
