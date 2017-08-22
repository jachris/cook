from cook import cpp

main = cpp.executable(
    name='main',
    sources=['main.cpp'],
    links=['boost_regex']
)
