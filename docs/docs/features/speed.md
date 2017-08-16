---
layout: docs
title: Speed
---

# Speed
{:.no_toc}

* TOC
{:toc}


## Introduction

While there isn't a detailed performance analysis at the moment, it should be
possible to show that Cook is quite fast by using an already existing project
and converting it to Cook. The following benchmarks were done building
[Ninja](https://github.com/ninja-build/ninja), which is a build-system
written in C++, using both Cook and Ninja itself. Ninja is one 
of the fastest build tools available, it was created for the Chromium 
project which suffered under slow build times. All tests were conducted using a 
best-of-five methodology running on 3 cores with 5 jobs.

Please note that `ninja` was run after the corresponding build script was
created by a configure script. This means that Cook has to perform more work
since it first figures out which compiler and compiler flags to use and so on.

One could suggest that the size of the Ninja codebase represents about the 
average project size. This may be true unless your projects include the Linux
Kernel, the Chromium project or anything else with many, many files. Cook does
currently not perform that well, although it definitely scales linearly with 
regards to the number of source files. We cannot currently recommend using
Cook for projects with more than 10000 source files. However this limit may
be lifted soon after performance critical subroutines are rewritten in C.


## Full Build

```bash
$ time sh -c 'rm -rf build/ && cook > /dev/null'
real    0m7.113s
user    0m17.292s
sys     0m1.404s

$ time sh -c 'rm -rf build/ && ninja > /dev/null'
real    0m7.058s
user    0m17.416s
sys     0m1.364s
```

A full build entails that every command is guaranteed to be run. Because of
that, the execution time is dominated by the compilation of the source files
and the relative differences are vanishingly small.


## Incremental Build

```bash
$ time sh -c 'touch src/state.cc && cook > /dev/null'

real    0m1.719s
user    0m1.524s
sys     0m0.120s

$ time sh -c 'touch src/state.cc && ninja > /dev/null'
real    0m1.534s
user    0m1.368s
sys     0m0.096s
```

Changing one `.cc` file on the other hand just means that every dependant 
command has to be redone. Changing `state.cc` invalidates a static library and
the main executable which is produced by linking against that library.


## Null Build

```bash
$ time sh -c 'cook > /dev/null'
real    0m0.285s
user    0m0.228s
sys     0m0.028s

$ time sh -c 'ninja > /dev/null'
real    0m0.013s
user    0m0.000s
sys     0m0.000s
```

When running without any modification compared to the previous run, the build 
system must still evaluate the build script and perform certain checks on the
filesystem. However the difference in time must of course not be interpreted 
proportionally to the project complexity, since Cook performs a relatively 
expensive, but constant-time setup before evaluation.
