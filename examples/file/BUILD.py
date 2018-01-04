from cook import file

file.copy(
    input='BUILD.py',
    output='MY_COPY.py'
)

ninja_zip = file.download(
    url='https://github.com/ninja-build/ninja/archive/v1.7.2.zip',
    destination='ninja.zip',
    sha256='6645230ae6cea71d095fa3b8992a30a58d967a65c931a779f07cbb62eaa39698'
)

file.extract(
    archive=ninja_zip.output,
    mapping={'ninja-1.7.2/README': 'ninja_readme'}
)
