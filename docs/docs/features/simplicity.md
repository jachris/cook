---
layout: docs
title: Simplicity
---

# Simplicity
{:.no_toc}

* TOC
{:toc}


## System

Counting the actual lines of code in `core` excluding comments and docstrings 
currently yields a result close to 900 lines. This is a joke compared to many
other systems and as a result the codebase can be understood in very little 
time. This could be useful to you if you want to know exactly what the system
does in circumstances which are not described in the documentation. It also
lowers the contribution barrier significantly.


## Language

One if not the currently most used build system is `CMake`, but it has one very
big problem: It's scripting language is awfully bad, a statement which is 
agreed upon by almost everyone. It was originally not designed to be a 
full-featured programming language, which is also why everything is a string
and control structures look very weird.

Fact is that you need a real programming language for everything but the most
simple build setups. Because of that, Cook uses the general-purpose programming
language Python, which means you get advanced data structures and functions
out-of-the-box. This however, has its downside: We do not really want to have
complexity where it is not needed. Because of that, all Cook rules are 
declarative by nature, because you just tell the rule what it should do and
that's it. This makes it very easy to reason about the outputs of these rules
as almost everything you need to know is in one place.


## Debuggability

Since everything is running inside the Python interpreter, you can set 
breakpoints and step through the code with existing tools. This greatly 
reduces the need for print-debugging and speeds up the rule development time.


## Interface

The commandline interface of Cook is straightforward.

```
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

Targets can be specified by using their filename. If you only want to build
a library and not the executable, you can pass it's filename like 
`cook libname.so`. You can also pass the full version like 
`cook build/libname.so`. 

Scripts using Cook can define options with various types. You can set these
easily using the commandline interface. Suppose there is an option named 
`count` and it is of type `int`, you can set it using `cook count=34`.

## API

While the API provided by the `core` subpackage is quite big in terms of number
of exposed symbols (there are about 30), there are basically 4 categories
which are listed below.

* Paths: `source`, `glob`, `which`, `absolute`, `relative`, `build`, `temporary`, `intermediate`
* Utility: `linux`, `mac`, `windows`, `checksum`, `call`, `random`, `cache`
* Logging: `debug`, `info`, `warning`, `error`
* System: `default`, `rule`, `publish`, `deposit`, `task`, `option`, `load`

Most of these should be self-explanatory. If you are not sure, take a look at 
the [core documentation]({% link docs/core.md %}).
