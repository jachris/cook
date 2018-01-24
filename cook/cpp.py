import os
import re

from . import core


@core.rule
def executable(
    name, sources=None, include=None, define=None, flags=None, links=None,
    compiler=None, warnings_are_errors=False, scan=True, debug=True,
    objects=None, linkflags=None
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
    objects = list(objects) if objects else []
    linkflags = list(linkflags) if linkflags else []

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
                if toolchain is GNU:
                    shared.append(core.resolve(link.output))
                else:
                    shared.append(core.resolve(link.msvc_lib))
            else:
                raise TypeError('invalid entry in links: "{}"'.format(link))

    if toolchain is MSVC:
        name += '.exe'
    name = core.build(name)

    for source in sources:
        obj = object(
            sources=[source],
            include=include,
            define=define,
            flags=flags,
            compiler=compiler,
            error_warnings=warnings_are_errors,
            scan=scan,
            debug=debug
        )
        objects.append(core.resolve(obj.output))

    yield core.publish(
        inputs=objects + static + shared,
        message='Link {}'.format(name),
        outputs=[name],
        result={
            'type': 'cpp.executable'
        },
        check=linkflags
    )

    if toolchain is GNU:
        command = [compiler, '-o', name]
        command.extend(objects)
        command.extend(static)
        for s in shared:
            command.append(s)
            command.append('-Wl,-rpath,' + os.path.dirname(core.absolute(s)))
        command.append('-lstdc++')
        command.extend(linkflags)
        core.call(command)
    elif toolchain is MSVC:
        command = [compiler, '/Fe' + name, '/nologo']
        command.extend(objects + shared + static)
        command.extend(linkflags)
        core.call(command, env=_msvc_get_cl_env(compiler))


@core.rule
def static_library(
    name=None, sources=None, include=None, define=None, flags=None,
    headers=None, compiler=None, warnings_are_errors=False, scan=True,
    debug=True, objects=None, linkflags=None
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
    if objects is None:
        objects = []
    linkflags = list(linkflags) if linkflags else []

    for source in sources:
        obj = object(
            sources=[source],
            compiler=compiler,
            scan=scan,
            include=include,
            define=define,
            flags=flags,
            error_warnings=warnings_are_errors,
            debug=debug
        )
        objects.append(obj.output)

    if name is None:
        name = core.intermediate(core.checksum(
            sources, compiler, toolchain, include, define, headers))
    else:
        name = core.build(name)

    if toolchain is MSVC:
        name += '.lib'
    elif toolchain is GNU:
        name += '.a'

    yield core.publish(
        inputs=objects,
        message='Static {}'.format(name),
        outputs=[name],
        result={
            'type': 'cpp.static_library',
            'headers': core.absolute(core.resolve(headers))
        },
        check=linkflags
    )

    if toolchain is GNU:
        archiver = core.which('ar')
        command = [archiver, 'rs', name]
        command.extend(objects)
        command.extend(linkflags)
        core.call(command)
    elif toolchain is MSVC:
        archiver = os.path.join(os.path.dirname(compiler), 'lib.exe')
        command = [archiver, '/OUT:' + name]
        command.extend(objects)
        command.extend(linkflags)
        core.call(command, env=_msvc_get_cl_env(compiler))


@core.rule
def shared_library(
    name, sources, include=None, define=None, flags=None, headers=None,
    compiler=None, warnings_are_errors=False, scan=True, msvc_lib=False,
    debug=True, linkflags=None
):
    if compiler is None:
        compiler, toolchain = _get_default_compiler()
    else:
        toolchain = _get_toolchain(compiler)
        if toolchain is None:
            raise ValueError('toolchain could not be detected')

    if headers is None:
        headers = []
    linkflags = list(linkflags) if linkflags else []

    if flags is None:
        flags = []
    if toolchain is GNU:
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
            error_warnings=warnings_are_errors,
            debug=debug
        )
        objects.append(obj.output)

    if toolchain is MSVC:
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
        check=linkflags
    )

    if toolchain is GNU:
        command = [compiler, '-shared', '-o', name]
        command.extend(objects)
        command.append('-Wl,-soname,' + os.path.basename(name))
        command.extend(linkflags)
        core.call(command)
    elif toolchain is MSVC:
        command = [compiler, '/Fe' + name, '/nologo', '/LD']
        command.extend(objects)
        command.extend(linkflags)
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
    compiler=None, error_warnings=False, scan=True, debug=True, depend=None
):
    if isinstance(sources, str):
        raise TypeError('sources must not be a string - try to use a list')
    if not sources:
        raise ValueError('sources must not be empty')

    sources = core.resolve(sources)
    include = list(include) if include else []
    define = dict(define) if define else {}
    flags = list(flags) if flags else []
    depend = list(depend) if depend else []

    if compiler is None:
        compiler, toolchain = _get_default_compiler()
    else:
        toolchain = _get_toolchain(compiler)
        if toolchain is None:
            raise ValueError('toolchain could not be detected')

    if name is None:
        name = core.intermediate(core.checksum(
            core.absolute(sources), compiler)[:16])
    else:
        name = core.build(name)

    if toolchain is GNU:
        name += '.o'
    elif toolchain is MSVC:
        name += '.obj'

    yield core.publish(
        inputs=sources + [compiler] + depend,
        message='Compile ' + ', '.join(sources),
        outputs=[name],
        check=[include, define, flags, error_warnings, scan, debug],
        result={
            'type': 'cpp.object',
            'include': include,
            'define': define,
            'flags': flags,
            'compiler': compiler,
        }
    )

    for identifier, value in define.items():
        if isinstance(value, str):
            define[identifier] = '"{}"'.format(value)
        elif value is True:
            define[identifier] = 'true'
        elif value is False:
            define[identifier] = 'false'
        elif isinstance(value, (int, float)):
            pass
        else:
            raise TypeError('unsupported define type: {}'.format(type(value)))

    if toolchain is GNU:
        command = [compiler, '-c', '-o', name, '-x', 'c++', '-std=c++11']
        command.extend(sources)

        for directory in include:
            command.extend(['-I', directory])

        # Enable most warnings. Option to change this?
        command.append('-Wall')
        if error_warnings:
            command.append('-Werror')

        if debug:
            command.append('-g')
        else:
            command.append('-O3')
            command.append('-DNDEBUG')

        for identifier, value in define.items():
            command.append('-D{}={}'.format(identifier, value))

        if scan:
            depfile = core.temporary(core.random('.d'))
            command.extend(['-MD', '-MF', depfile])
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
            # TODO: No difference!!
            used.difference_update(core.absolute(sources))
            used.difference_update(core.absolute(depend))
        else:
            used = None

        yield core.deposit(inputs=used, warnings=output or None)

    elif toolchain is MSVC:
        command = [compiler, '/c', '/Fo' + name, '/nologo']
        command.extend(sources)
        for directory in include:
            command.extend(['/I' + directory])

        if scan:
            command.append('/showIncludes')
        for identifier, value in define.items():
            command.append('/D{}={}'.format(identifier, value))

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
    if core.windows:
        return _find('{}.lib'.format(name))
    else:
        return _find('lib{}.a'.format(name))


def find_shared_library(name):
    if core.windows:
        return _find('{}.dll'.format(name))
    else:
        return _find('lib{}.so'.format(name))


def get_default_toolchain():
    return _get_default_compiler()[1]


GNU = 'GNU'
MSVC = 'MSVC'


def _find(name):
    if core.windows:
        env = _msvc_get_cl_env(_get_default_compiler()[0])
        for directory in env['LIB'].split(os.pathsep):
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                return path
    else:
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


@core.cache
def _get_default_compiler():
    compiler = os.environ.get('CXX')
    if compiler is not None:
        compiler = core.which(compiler)
        if compiler is None:
            raise FileNotFoundError('CXX compiler does not exist')
        toolchain = _get_toolchain(compiler)
    elif core.windows:
        compiler = _msvc_find_cl()
        toolchain = _get_toolchain(compiler)

    if compiler is None:
        compiler = core.which('c++') or core.which('g++')
        toolchain = _get_toolchain(compiler)

    if compiler is None:
        ValueError('compiler could not be determined')
    elif toolchain is None:
        raise ValueError('toolchain could not be detected')

    core.debug('Detected C++ compiler: {} [{}]'.format(compiler, toolchain))
    return compiler, toolchain


@core.cache
def _get_toolchain(compiler):
    if compiler is None:
        return None
    if 'g++' in compiler:
        return GNU
    if 'clang' in compiler:
        return GNU
    if 'cl.exe' in compiler:
        return MSVC


@core.cache
def _msvc_get_cl_env(cl):
    bat = os.path.normpath(
        os.path.join(os.path.dirname(cl), '../vcvarsall.bat'))
    if os.path.isfile(bat):
        return _msvc_extract_vcvars(bat)
    bat = os.path.normpath(os.path.join(
        os.path.dirname(cl),
        '../../../../../../Auxiliary/Build/vcvarsall.bat')
    )
    if os.path.isfile(bat):
        return _msvc_extract_vcvars(bat)
    raise ValueError('could not extract env')


@core.cache
def _msvc_extract_vcvars(vcvars):
    core.debug('Extracting environment of {}'.format(vcvars))
    helper = core.temporary(core.random('.bat'))
    with open(helper, 'w') as stream:
        stream.write('\n'.join([
            '@call "{vcvars}" {mode}',
            '@echo PATH=%PATH%',
            '@echo INCLUDE=%INCLUDE%',
            '@echo LIB=%LIB%;%LIBPATH%'
        ]).format(vcvars=vcvars, mode='x86'))
    cmd = core.which('cmd.exe')
    output = core.call([cmd, '/C', helper])
    env = os.environ.copy()
    steps = 0
    for line in output.strip().splitlines():
        if any(line.startswith(var) for var in ('PATH=', 'INCLUDE=', 'LIB=')):
            key, value = line.split('=', maxsplit=1)
            env[key] = value[:-1]
            steps += 1
    if steps != 3:
        raise RuntimeError('msvc auto configuration failed: {}' + output)
    return env


def _msvc_find_cl():
    path = os.path.join(
        os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'),
        r'Microsoft Visual Studio\2017\BuildTools\VC\Auxiliary\Build',
        'vcvarsall.bat'
    )
    if os.path.isfile(path):
        env = _msvc_extract_vcvars(path)
        cl = core.which('cl.exe', env=env)
        if cl is None:
            raise FileNotFoundError('expected to find cl')
        return cl

    for version in [140, 120, 110, 100, 90, 80, 71, 70]:
        tools = os.environ.get('VS{}COMNTOOLS'.format(version))
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


@core.cache
def _gnu_supports_colors(compiler):
    try:
        core.call([compiler, '-fdiagnostics-color'])
    except core.CallError as exc:
        return ('unknown argument' not in exc.output and
                'unrecognized command line option' not in exc.output)
