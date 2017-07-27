---
layout: docs
title: Getting Started
---

# Getting Started

Instructions for installation are available [here](/installation/).
Make sure that you have Cook installed for the following steps.

```
$ cook --help
Usage: cook <args> [target] [option=value] ...

Arguments:
  -h, --help         show this help message and exit
  -b, --build PATH   location of BUILD.py
  -j, --jobs INT     number of jobs (default: 5)
  -v, --verbose      enable debug mode
  -o, --output PATH  override build directory
  -r, --results
```

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

You should be able to build the program and execute it.

```
$ cook
[  0%] Compile main.cpp
[ 50%] Link build/hello
[100%] Done.

$ ./build/hello
Hello world!
```
