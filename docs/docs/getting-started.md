---
layout: docs
title: Getting Started
---

# Getting Started
{:.no_toc}

* TOC
{:toc}


## Installation

Instructions for installation are available 
[here]({% link docs/installation.md %}). Make sure that you have Cook installed 
for the following steps.

```
$ cook --help
Usage: cook <args> [target] [option=value] ...

Arguments:
  -h, --help         Show this help message and exit
  -b, --build PATH   Location of BUILD.py
  -j, --jobs INT     Number of jobs (default: 5)
  -v, --verbose      Enable debug mode
  -o, --output PATH  Override build directory
  --options          List all options and exit
  --targets          List all targets and exit
```

## Setup

Let's create a new C++ project using Cook.

```
$ mkdir cook-example/ 
$ cd cook-example/
```

For now we will just have one executable built from one source file.

```
$ cat > main.cpp <<EOF
#include <iostream>

int main() {
    std::cout << "Hello world!" << std::endl;
}
EOF
```

Next, we will create the build script:

```
$ cat > BUILD.py <<EOF
from cook import cpp

cpp.executable(
    name='hello',
    sources=['main.cpp']
)
EOF
```

## Result

You should be able to build the program and execute it.

```
$ cook
[  0%] Compile main.cpp
[ 50%] Link build/hello
[100%] Done.

$ ./build/hello
Hello world!
```

## Next Steps

If you are interested in creating custom rules, make sure to visit
[the tutorial]({% link docs/custom-rules.md %}). You can find more information
about the C++ rules [here]({% link docs/rules/cpp.md %}) or maybe take a look
at the [features]({% link docs/features/index.md %}) provided by Cook and the
[other rules]({% link docs/rules/index.md %})?
