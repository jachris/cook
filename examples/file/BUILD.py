from cook import file

file.copy(
    input='BUILD.py',
    output='MY_COPY.py'
)

file.download(
    url='https://github.com/ninja-build/ninja/archive/v1.7.2.zip',
    destination='ninja.zip',
    sha256='6645230ae6cea71d095fa3b8992a30a58d967a65c931a779f07cbb62eaa39698'
)
