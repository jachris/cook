---
title: Introduction to Cook
---

Welcome to the introductory blog post about Cook---a new build system. You are 
probably asking yourself: Why do we need yet another build system? As of now,
[Wikipedia lists close to 50 candidates](https://en.wikipedia.org/wiki/List_of_build_automation_software).
What in the world could Cook give you, that other build-systems do not?

Let's start with one simple observation: [All build systems suck](http://msoucy.me/seminars/bss/#(1)). 
While some may suck less, there is not a single one that's *really* great. And
let's be honest: Cook won't change this. There are just too many aspects about
building software, which makes building that one tool that fits
all purposes very difficult.

* TOC
{:toc}

**Note:** Cook is currently in version 0.2.0---which means a lot of things 
still need some work. Contributors are very welcome! Please help in making this
project a great build-system. Or just play a little bit around with the project
using the examples. Everything is appreciated.


## Motivation

Cook was created to address two specific problems:

- **Simplicity**. Most build-systems are so complex that even doing simple
  tasks inevitably lead to consulting Google and Stack Overflow. Some are even
  worse ([Autotools, \*cough\*](http://voices.canonical.com/jussi.pakkanen/2011/09/13/autotools/))
  and provoke a culture where everyone just copies build-scripts from other
  projects, makes little changes to address the differences between the projects
  until it somehow works---for that one developer at least. Others probably
  won't have fun using that hotchpotch. Oh, and let's just not talk about 
  CMake's monstrosity of a language.
  
  Additionally, most codebases are so
  complex that truly understanding the system is impossible: While you don't
  need to know how a car works in order to drive one, there should at least be 
  the possibility to understand how it works given enough interest and time.
  [Bazel](https://bazel.build/) clocks in at 3.3K Java files with a total size 
  of 26MB---and that's just counting the core (`bazel/src/`). 
  [CMake](https://cmake.org/) is about 1.75K `.cxx` or `.cmake` files which are
  about 11MB in total.
- **Extensibility**. Most of the common use-cases are supported by all major
  build-systems. They most often provide an API to define custom tasks as well.
  However, theses APIs could be a lot better. Wouldn't it be cool if one could
  just write custom tasks down linearly like they will be executed by the
  system? This is not about simple commands---it's about complex behaviours 
  which are at hand when dealing with non-trivial builds, i.e. returning the
  output of gcc's `-MD` (which lists all used files during the compilation) to
  the system.

Don't get me wrong: CMake and Bazel are really doing a good job. They are 
really powerful, having support for project generation for many IDEs, 
integrated packaging and testing or scalability. It just happens that their 
goals do not align well with some people's needs.

Cook currently has 21 source files with a total size of 0.073MB---including 
rules for C++, GIMP, LaTeX, LibreOffice and other misc miscellaneous rules. 
Extending it by writing a custom one is really easy.
  

## Hello World

Using Cook to compile a new C++ project is quite easy.

```c++
// File: hello.cpp
#include <iostream>

int main() {
    std::cout << "Hello world!" << std::endl;
}
```

The build-script looks like this:

```python
# File: BUILD.py
from cook import cpp

cpp.executable(
    name='hello',
    sources=['hello.cpp']
)
```

We are importing the `cpp` package here since we want to build a c++ 
`executable`.

```
$ cook
[  0%] Compile main.cpp
[ 50%] Link build/hello
[100%] Done.

$ ./build/hello
Hello world!
```

**Note:** This works Linux and Windows. MacOS is currently
untested but it should work as well.


## Advanced Examples

Putting source files belonging to a certain module or library in their own
shared folder is a common pattern. This structure is nicely represented using
glob patterns, such as:

```python
from cook import cpp, core

cpp.static_library(
    name='foo',
    sources=core.glob('*.cpp')
)
```

Sometimes you want to enable or disable certain features of your application 
during compilation, for example when having a lite and professional version.
Cook allows declaring options of various types which can be set upon 
invocation.

```python
from cook import cpp, core

lite = core.option('lite', help='build lite version instead of professional')

cpp.executable(
    name='app',
    sources=core.glob('*.cpp'),
    define={
        'LITE': lite
    },
    links=['boost_regex', 'boost_utils']
)
```

Building the lite version is now performed using `cook lite=1`, while the 
professional version will be built as usual: `cook`. You can also list all
available options:

```
$ cook --options
name       type  default    help                
----------------------------------------------------------------------
lite       bool  True       build lite version instead of professional
```


## Custom Rules

Here is a little snippet showing a rule which replaces occurrences of a string 
with another.

```python
from cook import core

@core.rule
def replace(source, destination, mapping):
    source = core.source(source)
    destination = core.build(destination)

    yield core.publish(
        inputs=[source],
        message='Processing {}'.format(source),
        outputs=[destination],
        check=mapping
    )

    with open(source) as file:
        content = file.read()
    for key, value in mapping.items():
        content = content.replace(key, value)
    with open(destination, 'w') as file:
        file.write(content)
        
year = core.option('year', int, 1979, 'overwrite the year of publication')
        
replace(
    source='foo.txt',
    destination='out.txt',
    mapping={
        'meaning of life': 42,
        'author': 'Douglas Adams',
        'year': year
    }
)
```

Just a few words on how this works: `core.source` and `core.build` interpret
the following path relative to the currently evaluated build-script 
respectively the build directory. The `yield` statement pauses execution of the
rule---it will continue if and when the system decides it should. The `mapping`
is passed using the `check` keyword argument. This will make the system look at
the `mapping` and detect if it changed after the last run, because then it must 
be redone.

If you want to know more about creating custom rules, make sure to 
[check out the docs](/docs/custom-rules/).


## Some Additional Features

- Compiler warnings are emitted and stored for the following builds in order
  to re-emit them without recompiling. This guarantees correctness.
- Automatically detects libraries on all operating systems.
- Sane language. Python is arguably one of the most concise and best-to-read 
  languages currently available. Since Cook is 100% Python, you can also use
  a debugger to inspect tasks when custom rules break.  
- While C++ rules are the most stable for now, there are already rules for 
  general file handling, downloading, LaTeX documents (very basic), LibreOffice
  and GIMP export. The last three make creating documents which include 
  graphics produced by LibreOffice or GIMP much easier.
- Support for Microsoft Visual Compiler (not Studio) 2005--2017.
- Basic IDE project generation is in the works. However, the IDE must still 
  call Cook for doing the build---which means no MSBuild.
- Other build-scripts can be imported using `core.load()`.
- The state of the build tree is also looked at when considering which tasks to
  run. You could even go ahead and edit the resulting build files without 
  breaking subsequent builds.


## Closing Words

We hope to have given you a brief overview about the project. This was in no 
way an article covering the whole spectrum of things to be said, but if we 
caught your interest, then you can take a look at the 
[GitHub repository](https://github.com/jachris/cook). While not all parts are
great from a coding-style point of view, it is hopefully enough polished to get
you started. Feel free to 
[open an issue](https://github.com/jachris/cook/issues) or maybe even upload a 
pull request. Your help is very much appreciated.

If you need more information about Cook, make sure to [read more about its 
features](/docs/features/).
