from cook import core, cpp

utils = cpp.shared_library(
    name='utils',
    sources=core.glob('utils/*.cpp'),
)

cpp.executable(
    name='main',
    sources=core.glob('main/*.cpp'),
    link=[utils, 'boost_regex']
)
