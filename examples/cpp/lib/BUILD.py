from cook import core, cpp

bar = cpp.static_library(
    sources=['bar.cpp'],
    headers=['.'],
)
