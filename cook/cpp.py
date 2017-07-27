import os
import re
import threading

from . import core


@core.rule
def executable(
    name, sources=None, include=None, define=None, flags=None,
    links=None, compiler=None, warnings_are_errors=False, scan=True
):
    if compiler is None:
        compiler, toolchain = _get_default_compiler()
    else:
        toolchain = _get_toolchain(compiler)
        if toolchain is None:
            raise ValueError('toolchain could not be detected')

    include = list(include) if include else []
    define = dict(define) if define else {}
    flags = list(flags) if flags else []

    static = []
    shared = []

    if links:
        for link in links:
            if isinstance(link, str):
                lib = find_static_library(link)
                if lib is None:
                    raise ValueError('lib could not be found: ' + link)
                static.append(lib)
            elif getattr(link, 'type') == 'cpp.static_library':
                include.extend(link.headers)
                static.append(core.resolve(link.output))
            elif getattr(link, 'type') == 'cpp.shared_library':
                include.extend(link.headers)
                if toolchain is _GNU:
                    shared.append(core.resolve(link.output))
                else:
                    shared.append(core.resolve(link.msvc_lib))
            else:
                raise TypeError('invalid entry in links: "{}"'.format(link))

    if toolchain is _MSVC:
        name += '.exe'
    name = core.build(name)

    objects = []
    for source in sources:
        obj = object(
            sources=[source],
            include=include,
            define=define,
            flags=flags,
            compiler=compiler,
            error_warnings=warnings_are_errors,
            scan=scan,
        )
        objects.append(core.resolve(obj.output))

    yield core.publish(
        inputs=objects + static + shared,
        message='Link {}'.format(name),
        outputs=[name],
        result={
            'type': 'cpp.executable'
        }
    )

    if toolchain is _GNU:
        command = [compiler, '-o', name]
        command.extend(objects)
        command.extend(static)
        for s in shared:
            command.append(s)
            command.append('-Wl,-rpath,' + os.path.dirname(core.absolute(s)))
        command.append('-lstdc++')
        core.call(command, env=os.environ)
    elif toolchain is _MSVC:
        command = [compiler, '/Fe' + name, '/nologo']
        command.extend(objects + shared + static)
        core.call(command, env=_msvc_get_cl_env(compiler))


@core.rule
def static_library(
    name=None, sources=None, include=None, define=None, flags=None,
    headers=None, compiler=None, warnings_are_errors=False, scan=True
):
    if compiler is None:
        compiler, toolchain = _get_default_compiler()
    else:
        toolchain = _get_toolchain(compiler)
        if toolchain is None:
            raise ValueError('toolchain could not be detected')

    if headers is None:
        headers = []
    if sources is None:
        sources = []

    objects = []
    for source in sources:
        obj = object(
            sources=[source],
            compiler=compiler,
            scan=scan,
            include=include,
            define=define,
            flags=flags,
            error_warnings=warnings_are_errors
        )
        objects.append(obj.output)

    if name is None:
        name = core.intermediate(core.checksum(
            sources, compiler, toolchain, include, define, headers))
    else:
        name = core.build(name)

    if toolchain is _MSVC:
        name += '.lib'
    elif toolchain is _GNU:
        name += '.a'

    yield core.publish(
        inputs=objects,
        message='Static {}'.format(name),
        outputs=[name],
        result={
            'type': 'cpp.static_library',
            'headers': core.absolute(core.resolve(headers))
        }
    )

    if toolchain is _GNU:
        archiver = core.which('ar')
        command = [archiver, 'rs', name]
        command.extend(objects)
        core.call(command)
    elif toolchain is _MSVC:
        archiver = os.path.join(os.path.dirname(compiler), 'lib.exe')
        command = [archiver, '/OUT:' + name]
        command.extend(objects)
        core.call(command)


@core.rule
def shared_library(
    name, sources, include=None, define=None, flags=None, headers=None,
    compiler=None, warnings_are_errors=False, scan=True, msvc_lib=False
):
    if compiler is None:
        compiler, toolchain = _get_default_compiler()
    else:
        toolchain = _get_toolchain(compiler)
        if toolchain is None:
            raise ValueError('toolchain could not be detected')

    if headers is None:
        headers = []

    if flags is None:
        flags = []
    if toolchain is _GNU:
        flags.append('-fPIC')

    if define is None:
        define = {}
    define['DLL_EXPORT'] = 1

    objects = []
    for source in sources:
        obj = object(
            sources=[source],
            compiler=compiler,
            scan=scan,
            include=include,
            define=define,
            flags=flags,
            error_warnings=warnings_are_errors
        )
        objects.append(obj.output)

    if toolchain is _MSVC:
        lib = name + '.lib'
        if msvc_lib:
            lib = core.build(lib)
        else:
            lib = core.intermediate(lib)
        name = core.build(name + '.dll')
    else:
        lib = None
        head, tail = os.path.split(name)
        name = core.build(os.path.join(head, 'lib' + tail + '.so'))

    yield core.publish(
        inputs=objects,
        message='Shared {}'.format(name),
        outputs=[name, lib] if lib else [name],
        result={
            'type': 'cpp.shared_library',
            'msvc_lib': core.absolute(lib),
            'headers': core.absolute(core.resolve(headers)),
            'output': core.absolute(name)
        },
    )

    if toolchain is _GNU:
        command = [compiler, '-shared', '-o', name]
        command.extend(objects)
        command.append('-Wl,-soname,' + os.path.basename(name))
        core.call(command, env=os.environ)
    elif toolchain is _MSVC:
        command = [compiler, '/Fe' + name, '/nologo', '/LD']
        command.extend(objects)
        core.call(command, env=_msvc_get_cl_env(compiler))
        base = os.path.splitext(name)[0]
        if not msvc_lib:
            origin = base + '.lib'
            if os.path.isfile(lib):
                os.remove(lib)
            os.rename(origin, lib)
        os.remove(base + '.exp')
    else:
        raise NotImplementedError


@core.rule
def object(
    name=None, sources=None, include=None, define=None, flags=None,
    compiler=None, error_warnings=False, scan=True
):
    if isinstance(sources, str):
        raise TypeError('sources must not be a string - try to use a list')
    if not sources:
        raise ValueError('sources must not be empty')

    sources = core.resolve(sources)
    include = list(include) if include else []
    define = dict(define) if define else {}
    flags = list(flags) if flags else []

    if compiler is None:
        compiler, toolchain = _get_default_compiler()
    else:
        toolchain = _get_toolchain(compiler)
        if toolchain is None:
            raise ValueError('toolchain could not be detected')

    if name is None:
        name = core.intermediate(core.checksum(
            core.absolute(sources), compiler)[:16])

    if toolchain is _GNU:
        name += '.o'
    elif toolchain is _MSVC:
        name += '.obj'

    yield core.publish(
        inputs=sources + [compiler],
        message='Compile ' + ', '.join(sources),
        outputs=[name],
        check=[include, define, flags, error_warnings, scan],
        result={
            'type': 'cpp.object',
            'include': include,
            'define': define,
            'flags': flags,
            'compiler': compiler,
        }
    )

    if toolchain is _GNU:
        command = [compiler, '-c', '-o', name, '-x', 'c++', '-std=c++11']
        command.extend(sources)

        for directory in include:
            command.extend(['-I', directory])

        # Enable most warnings. Option to change this?
        command.append('-Wall')
        if error_warnings:
            command.append('-Werror')

        # Generate debug information... Option to turn this off?
        command.append('-g')

        for name, value in define.items():
            command.append('-D{}={}'.format(name, value))

        if scan:
            depfile = core.temporary(core.random('.d'))
            command.extend(['-MMD', '-MF', depfile])
        else:
            depfile = None

        if _gnu_supports_colors(compiler):
            command.append('-fdiagnostics-color')

        command.extend(flags)

        output = core.call(command)

        if scan:
            # TODO: Good parsing.
            with open(depfile) as file:
                content = file.read()
            used = {
                os.path.abspath(x) for x in
                content[content.find(':')+1:].replace('\\\n', '\n').split()
            }
            used.difference_update(sources)  # TODO: No difference?
        else:
            used = None

        yield core.deposit(inputs=used, warnings=output or None)

    elif toolchain is _MSVC:
        command = [compiler, '/c', '/Fo' + name, '/nologo']
        command.extend(sources)
        for directory in include:
            command.extend(['/I' + directory])

        if scan:
            command.append('/showIncludes')
        for name, value in define.items():
            command.append('/D{}={}'.format(name, value))

        # TODO: Option to set c++ standard.
        # command.append('/std:' + standard)

        # TODO: Figure out debug / relase
        # === DEBUG ===
        # command.append('/ZI')  Enable nice debug mode?
        # command.append('/Od')  Disable optimizations for debug
        # command.append('/Gm')  Enable minimal rebuild?
        # command.append('/RTC1') Run-time error checks
        # /MDd
        # === RELEASE ===
        # command.append('/Ox')  Full Optimization or /Oi?
        # /Zi                    Debug information
        # /GL                    Breaks object-linking? Whole prog optimization
        # command.append('/O2')  Optimize for speed

        command.append('/W4')  # Enable most warnings.
        if error_warnings:
            command.append('/WX')  # All warnings as errors.
        command.append('/EHsc')  # Specify exception handling model
        command.append('/sdl')  # Additional security warnings
        command.append('/TP')  # Assume C++ sources
        command.extend(flags)

        try:
            output = core.call(command, env=_msvc_get_cl_env(compiler))
        except core.CallError as exc:
            exc.output = _msvc_strip_includes(exc.output)
            raise

        if scan:
            used = _msvc_extract_includes(output)
        else:
            used = None

        yield core.deposit(
            inputs=used,
            warnings=_msvc_strip_includes(output).strip() or None
        )


def find_static_library(name):
    return _find('lib{}.a'.format(name))


def find_shared_library(name):
    return _find('lib{}.so'.format(name))


_GNU = 'GNU'
_MSVC = 'MSVC'

_compiler = None
_toolchain = None
_prepare_lock = threading.Lock()
_prepared = False

_msvc_envs = {}
_msvc_envs_lock = threading.Lock()
_gnu_color_support = {}
_gnu_color_lock = threading.Lock()


def _find(name):
    architectures = ['x86_64-linux-gnu', 'i386-linux-gnu']
    env_path = os.environ.get('PATH', '').split(os.pathsep)
    for directory in env_path:
        if directory.endswith('bin') or directory.endswith('sbin'):
            directory = os.path.normpath(os.path.dirname(directory))
        for arch in architectures:
            path = os.path.join(directory, 'lib', arch, name)
            if os.path.isfile(path):
                return path
            path = os.path.join(directory, arch, name)
            if os.path.isfile(path):
                return path
        path = os.path.join(directory, 'lib', name)
        if os.path.isfile(path):
            return path
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            return path


def _get_default_compiler():
    if not _prepared:
        with _prepare_lock:
            if not _prepared:
                _do_get_default_compiler()
    return _compiler, _toolchain


def _do_get_default_compiler():
    global _compiler, _toolchain, _prepared

    _compiler = os.environ.get('CXX')
    if _compiler is not None:
        _compiler = core.which(_compiler)
        if _compiler is None:
            raise FileNotFoundError('CXX compiler does not exist')
        _toolchain = _get_toolchain(_compiler)
    elif core.windows:
        _compiler = _msvc_find_cl()
        _toolchain = _get_toolchain(_compiler)
    if _compiler is None:
        _compiler = core.which('c++') or core.which('g++')
        _toolchain = _get_toolchain(_compiler)

    if _compiler is None or _toolchain is None:
        ValueError('compiler could not be determined')

    core.debug('Detected C++ compiler: {} [{}]'.format(_compiler, _toolchain))
    _prepared = True


def _get_toolchain(compiler):
    if compiler is None:
        return None
    if 'g++' in compiler:
        return _GNU
    if 'clang' in compiler:
        return _GNU
    if 'cl.exe' in compiler:
        return _MSVC


def _msvc_get_cl_env(cl):
    with _msvc_envs_lock:
        if cl in _msvc_envs:
            return _msvc_envs[cl]
        else:
            env = _msvc_extract_env(cl)
            _msvc_envs[cl] = env
            return env


def _msvc_extract_env(cl):
    core.debug('Extracting environment for {}'.format(cl))
    bat = os.path.normpath(
        os.path.join(os.path.dirname(cl), '../vcvarsall.bat'))
    if not os.path.isfile(bat):
        return None
    helper = core.temporary(core.random('.bat'))
    with open(helper, 'w') as stream:
        stream.write('\n'.join([
            '@call "{bat}" {mode}',
            '@echo PATH=%PATH%',
            '@echo INCLUDE=%INCLUDE%',
            '@echo LIB=%LIB%;%LIBPATH%'
        ]).format(bat=bat, mode='x86'))
    cmd = core.which('cmd.exe')
    output = core.call([cmd, '/C', helper], env=os.environ)
    env = os.environ.copy()
    for line in output.strip().splitlines():
        key, value = line.split('=', maxsplit=1)
        env[key] = value[:-1]
    return env


def _msvc_find_cl():
    for version in ['120']:
        tools = os.environ.get('VS' + version + 'COMNTOOLS')
        if not tools:
            continue
        cl = os.path.normpath(os.path.join(tools, '../../VC/bin/cl.exe'))
        if os.path.isfile(cl):
            return cl


def _msvc_strip_includes(output):
    regex = re.compile(r'^[^:]+: [^:]+: +(.*)$')
    result = []
    for line in output.splitlines():
        match = regex.match(line)
        if match:
            path = match.group(1)
            if not os.path.isfile(path):
                result.append(line)
    return '\n'.join(result) + '\n'


def _msvc_extract_includes(output):
    regex = re.compile(r'^[^:]+: [^:]+: +(.*)$')
    used = []
    for line in output.splitlines():
        match = regex.match(line)
        if match:
            path = match.group(1)
            if os.path.isfile(path):
                used.append(path)
    return used


def _gnu_supports_colors(compiler):
    if compiler in _gnu_color_support:
        return _gnu_color_support[compiler]
    with _gnu_color_lock:
        if compiler in _gnu_color_support:
            return _gnu_color_support[compiler]
        try:
            core.call([compiler, '-fdiagnostics-color'])
        except core.CallError as exc:
            result = ('unrecognized command line option' not in exc.output
                      and 'unknown argument' not in exc.output)
            _gnu_color_support[compiler] = result
            return result
