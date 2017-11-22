import os
import re

from . import core, cpp

_sdk = os.environ.get('ANDROID_HOME')
_ndk = os.environ.get('ANDROID_NDK_HOME')
_java = os.environ.get('JAVA_HOME')

if _sdk:
    _build_tools = os.path.join(_sdk, 'build-tools', '25.0.3')
    _android = os.path.join(_sdk, 'platforms', 'android-25', 'android.jar')
    _aapt = os.path.join(_build_tools, 'aapt.exe')
    _align = os.path.join(_build_tools, 'zipalign.exe')
    _dx = os.path.join(_build_tools, 'dx.bat')
    _adb = os.path.join(_sdk, 'platform-tools', 'adb.exe')
else:
    _build_tools = None
    _android = None
    _aapt = None
    _align = None
    _dx = None
    _adb = None

_aarch64 = os.path.join(
    _ndk, 'toolchains', 'aarch64-linux-android-4.9', 'prebuilt',
    'windows-x86_64', 'bin', 'aarch64-linux-android-g++.exe'
)
_arm = os.path.join(
    _ndk, 'toolchains', 'arm-linux-androideabi-4.9', 'prebuilt',
    'windows-x86_64', 'bin', 'arm-linux-androideabi-g++.exe'
)
_x86 = os.path.join(
    _ndk, 'toolchains', 'x86-4.9', 'prebuilt', 'windows-x86_64', 'bin',
    'i686-linux-android-g++.exe'
)
_x86_64 = os.path.join(
    _ndk, 'toolchains', 'x86_64-4.9', 'prebuilt', 'windows-x86_64', 'bin',
    'x86_64-linux-android-g++.exe'
)
_mips = os.path.join(
    _ndk, 'toolchains', 'mipsel-linux-android-4.9', 'prebuilt', 'windows-x86_64', 'bin',
    'mipsel-linux-android-g++.exe'
)
_mips64 = os.path.join(
    _ndk, 'toolchains', 'mips64el-linux-android-4.9', 'prebuilt',
    'windows-x86_64', 'bin',
    'mips64el-linux-android-g++.exe'
)

if _java:
    _javac = os.path.join(_java, 'bin', 'javac.exe')
    _signer = os.path.join(_java, 'bin', 'jarsigner.exe')
else:
    _javac = None
    _signer = None

_archs = (
    (_arm, 'arm', 'armeabi'),
    (_x86, 'x86', 'x86'),
    (_aarch64, 'arm64', 'arm64-v8a'),
    (_x86_64, 'x86_64', 'x86_x64'),
    (_mips, 'mips', 'mips'),
    (_mips64, 'mips64', 'mips64')
)


@core.rule
def native_app(name, sources=None, archs=None):
    libs = []

    if archs is None:
        archs = ['arm', 'x86', 'arm64', 'x86_64', 'mips', 'mips64']

    lib_dir = core.absolute(core.intermediate(core.checksum(name)))
    for compiler, arch, identifier in _archs:
        if arch not in archs:
            continue
        sysroot = r'--sysroot={}/platforms/android-21/arch-{}'.format(
            _ndk, arch)
        lib = cpp.shared_library(
            name=r'{}/lib/{}/{}'.format(lib_dir, identifier, name),
            sources=sources,
            compiler=compiler,
            flags=['-std=c++11', sysroot],
            linkflags=[sysroot, '-llog', '-landroid', '-lGLESv2']
        )
        libs.append(lib.output)

    name = core.build(name + '.apk')
    manifest = core.source('AndroidManifest.xml')
    res = core.source('res')

    with open(manifest) as file:
        content = file.read()

    result = re.search(r'<manifest\spackage="([a-zA-Z0-9.]+)"', content)
    if result is None:
        raise ValueError('could not determine package name')
    package = result.group(1)

    yield core.publish(
        inputs=libs + [manifest] + core.glob(res + '/**'),
        outputs=[name],
        message='Building APK {}'.format(name),
        result=dict(
            package=package
        )
    )

    res_dir = core.temporary(core.random())
    os.mkdir(res_dir)

    res_cmd = [
        _aapt, 'package', '-M', manifest, '-I', _android,
        '-S', res, '-J', res_dir, '-m', '-f'
    ]
    core.call(res_cmd)
    r = os.path.join(res_dir, *package.split('.'), 'R.java')

    cls_dir = core.temporary(core.random())
    os.mkdir(cls_dir)

    clspath = ';'.join([_android, cls_dir, res_dir])
    srcpath = core.source('src')

    comp_cmd = [
        _javac, '-d', cls_dir, '-classpath', clspath,
        '-sourcepath', srcpath, r, '-source', '1.7', '-target', '1.7'
    ]
    core.call(comp_cmd)

    dex_dir = core.temporary(core.random())
    os.mkdir(dex_dir)
    cls_dex = os.path.join(dex_dir, 'classes.dex')

    core.call([_dx, '--dex', '--output=' + cls_dex, cls_dir])

    unsigned = core.temporary(core.random('_unsigned.apk'))
    command = [
        _aapt, 'package', '-f', '-M', manifest, '-S', res, '-I', _android,
        '-F', unsigned, dex_dir, lib_dir
    ]
    core.call(command)

    signed = core.temporary(core.random('_signed.apk'))

    keys = os.path.expanduser('~/.android/debug.keystore')
    core.call([
        _signer, '-keystore', keys, '-storepass', 'android', '-keypass',
        'android', '-signedjar', signed, unsigned,
        '-sigalg', 'SHA1withRSA', '-digestalg', 'SHA1',  # TODO: REMOVE
        'androiddebugkey'
    ])

    core.call([
        _align, '-f', '4', signed, name
    ])


@core.rule
def install(name, app, launch=False):
    apk = core.source(app.output)

    yield core.publish(
        inputs=[apk],
        message='Installing APK ...',
        outputs=[name],
        phony=True,
        force=True
    )

    core.call([
        _adb, 'install', '-r', apk
    ])

    if launch:
        core.call([
            _adb, 'shell', 'monkey', '-p', app.package, '1'
        ])
