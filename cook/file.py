import hashlib
import os
import shutil
import tarfile
import zipfile
from urllib.request import urlopen

from . import core


@core.rule
def extract(archive, mapping):
    core.resolve(archive)

    yield core.publish(
        inputs=[archive],
        outputs=core.build(mapping.values()),
        message='Extracting {}'.format(archive)
    )

    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zip:
            for path, destination in mapping.items():
                with zip.open(path) as member:
                    with open(core.build(destination), 'wb') as output:
                        shutil.copyfileobj(member, output)
    elif tarfile.is_tarfile(archive):
        with tarfile.open(archive) as tar:
            for path, destination in mapping.items():
                with tar.extractfile(path) as member:
                    with open(core.build(destination), 'wb') as output:
                        shutil.copyfileobj(member, output)
    else:
        raise ValueError('Unsupported file: ' + archive)


@core.rule
def copy(input, output):
    input = core.resolve(input)
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
    source = core.resolve(source)

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
def download(url, sha256=None, destination=None):
    if destination is None:
        destination = core.intermediate(os.path.basename(url))
    else:
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
    if sha256 is None:
        yield core.deposit(
            warnings='Downloaded "{}" without verification. \n'
                     'sha256={}'.format(url, checksum)
        )
    elif sha256 != 'IGNORE' and checksum != sha256:
        raise ValueError('Expected SHA256 {}, got {}'.format(sha256, checksum))
