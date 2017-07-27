from cook import core, cpp

lib = core.load('lib')
slib = core.load('slib')

foo = core.option('foo', type=int, default=5, help='define foo constant')

main = cpp.executable(
    name='main',
    sources=['main.cpp'],
    links=[lib.bar, slib.baz],
    define={'FOO': foo},
)
