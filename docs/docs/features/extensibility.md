---
layout: docs
title: Extensibility
---

# Extensibility
{:.no_toc}

* TOC
{:toc}

## The Problem

If you want to do something that the original authors of your build system did 
not foresee, you sometimes have to resort to suboptimal methods. 
This might not be good enough and you want to have the full power available to 
the internal rules of the build system. In Cook, the internal rules are using 
the same API as custom ones would use. This means that you are not restricted 
to just running a command, but instead have the full arsenal of useful features 
available, so that you can easily add support for new languages or other kind
of rules.

Take a look at [how to create custom rules]({% link docs/custom-rules.md %}).


## Example

Suppose there were no builtin rules for the C++ programming language (there 
are). You want to write one and it should support all popular compilers.
You also want to use the functionality provided by the compiler that lists the
header files that were including during the current compilation. This would be
`-MD -MF deps.d` for the GNU Compiler and `/showIncludes` for MSVC. Providing
these flags dependant on which compiler was being chosen would probably not be
a problem for most systems. However, there is an other one: The GCC version
outputs a Makefile from which you can extract the used files, while the MSVC
version prints the included files to the standard output which looks like 
`Note: including file: foo.h`. You would have to parse these outputs and tell
your build system, which files were being used, which --- depending on the
built system used --- might be very difficult or even impossible. Using Cook
you simply add `yield core.deposit(inputs=<includes here>)` to your rule.
