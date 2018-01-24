import os
import shutil

from . import core


@core.rule
def cmake(directory, retrieve):
    if not isinstance(retrieve, dict):
        retrieve = {core.build(x): x for x in retrieve}

    directory = core.absolute(core.resolve(directory))
    contents = core.glob(os.path.join(directory, '**'))
    exe = core.which('cmake')

    yield core.publish(
        inputs=contents,
        outputs=retrieve.keys(),
        message='Running CMake',
        check=list(retrieve.values()) + [directory]
    )

    temp = core.temporary(core.random())
    os.mkdir(temp)
    core.call([exe, directory], cwd=temp, env=os.environ)
    core.call([exe, '--build', '.'], cwd=temp, env=os.environ)

    for file in retrieve:
        source = os.path.join(temp, retrieve[file])
        os.rename(source, file)


@core.rule
def ninja(directory, retrieve):
    if not isinstance(retrieve, dict):
        retrieve = {core.build(x): x for x in retrieve}

    directory = core.absolute(core.resolve(directory))
    contents = core.glob(os.path.join(directory, '**'))
    exe = core.which('ninja')

    yield core.publish(
        inputs=contents,
        outputs=retrieve.keys(),
        message='Running Ninja',
        check=list(retrieve.values()) + [directory]
    )

    temp = core.temporary(core.random())
    shutil.copytree(directory, temp)
    core.call([exe], cwd=temp, env=os.environ)

    for file in retrieve:
        source = os.path.join(temp, retrieve[file])
        os.rename(source, file)


@core.rule
def make(directory, retrieve):
    if not isinstance(retrieve, dict):
        retrieve = {core.build(x): x for x in retrieve}

    directory = core.absolute(core.resolve(directory))
    contents = core.glob(os.path.join(directory, '**'))
    exe = core.which('make')

    yield core.publish(
        inputs=contents,
        outputs=retrieve.keys(),
        message='Running Make',
        check=list(retrieve.values()) + [directory]
    )

    temp = core.temporary(core.random())
    shutil.copytree(directory, temp)
    core.call([exe], cwd=temp, env=os.environ)

    for file in retrieve:
        source = os.path.join(temp, retrieve[file])
        os.rename(source, file)


@core.rule
def cook(directory, retrieve):
    if not isinstance(retrieve, dict):
        retrieve = {core.build(x): x for x in retrieve}

    directory = core.absolute(core.resolve(directory))
    contents = core.glob(os.path.join(directory, '**'))
    exe = core.which('cook')

    yield core.publish(
        inputs=contents,
        outputs=retrieve.keys(),
        message='Running Cook',
        check=list(retrieve.values()) + [directory]
    )

    temp = core.temporary(core.random())
    os.mkdir(temp)
    core.call([exe, '-o', temp], cwd=directory, env=os.environ)

    for file in retrieve:
        source = os.path.join(temp, retrieve[file])
        os.rename(source, file)
