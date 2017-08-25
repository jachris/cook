from cook import cpp

cpp.executable(
    name='main',
    sources=['main.cpp'],
    links=['user32']
)
