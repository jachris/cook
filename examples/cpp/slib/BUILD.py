from cook import cpp

baz = cpp.shared_library(
    name='baz',
    sources=['baz.cpp'],
    headers=['.'],
)
