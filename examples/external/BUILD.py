from cook import external

external.ninja(
    directory='ninja',
    retrieve=['foo']
)

external.cmake(
    directory='cmake',
    retrieve=['bar']
)

external.make(
    directory='make',
    retrieve=['baz']
)

external.cook(
    directory='cook',
    retrieve=['qux']
)
