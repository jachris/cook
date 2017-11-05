# [Cook — A Modern Build System](https://getcook.org/)

[![Travis](https://api.travis-ci.org/jachris/cook.svg)](https://travis-ci.org/jachris/cook)
[![AppVeyor](https://ci.appveyor.com/api/projects/status/github/jachris/cook?svg=true)](https://ci.appveyor.com/project/jachris/cook)

:zap: **This software is currently alpha and not ready for production use.**

:heart: **Contributions to this project are very welcome!**


## Overview

Cook is an extensible, dynamic, parallel and cross-platform
build system. It is based on the concept that writing build definitions should
be as powerful and easy as possible, which is why everything in Python. While 
many other systems may be slightly faster in benchmarks, we believe that, at 
least for most projects, these differences do not outweigh the advantages you 
get by using a more powerful system.


## Example

Using the built-in rules is straightforward. You just import the corresponding 
module and call the supplied rule. This is all you need to get a working build 
going. The following example will automatically work on any supported platform.

```python
from cook import cpp

cpp.executable(
    sources=['main.cpp'],
    destination='main'
)
```

Executing this script will build an executable using the correct 
platform-specific details. For example, the output is either named `main` or 
`main.exe` depending on the operating system.

```
$ ls
BUILD.py  main.cpp  main.h
$ cook
[  0%] Compile main.cpp
[ 50%] Link build/main
[100%] Done.
$ ls build/
main
```

You can also easily create your own rules. Upon calling, they are executed 
until the required information is passed back to the system using 
`yield core.publish(...)`. Everything after that is executed shortly after if 
the system decides it is necessary to do so.

```python
from cook import core

@core.rule
def replace(source, destination, mapping):
    source = core.source(source)
    destination = core.build(destination)

    yield core.publish(
        inputs=[source],
        message='Generating {}'.format(destination),
        outputs=[destination],
        check=mapping
    )
    
    with open(source) as file:
        content = file.read()
    for key, value in mapping.items():
        content = content.replace(key, value)
    with open(destination, 'w') as file:
        file.write(content)
```

Please look at [the documentation](https://getcook.org/docs/) if you want to
know more.
