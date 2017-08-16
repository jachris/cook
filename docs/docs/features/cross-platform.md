---
layout: docs
title: Cross Platform
---

# Cross Platform
{:.no_toc}

* TOC
{:toc}

## Overview

Cook was designed to be cross platform from ground up. This means that all
builtin rules should work on every supported platform. While the project is
still in alpha phase, a lot of this already works. However, there is still some
work to do, so you are invited to contribute.

The builtin C++ rules choose the appropriate compiler and its invocation 
without manual intervention by the user. For example: With most build systems,
you have to activate the MSVC yourself by executing a certain batch script 
provided by Microsoft which sets everything up. However, Cook automatically 
searches for this, tries to find the newest MSVC version and extracts the 
information provided by this batch script. Additionally, libraries should be
automatically discovered on every platform. The goal is that you do not have
to worry about platform-specific details at all, unless you want to manually 
set specialized compiler flags the rules do not know about. By querying which
compiler toolchain is being used, users can take care about this themselves as 
a last resort.


## Examples

* Cook automatically chooses the correct suffix depending on the toolchain, 
  which means you get `.exe` Windows executables and `.so` or `.dll` shared
  libraries depending on the platform.
* It also takes care of most compiler flags, setting up appropriate warning
  flags, `-Wall` or `/W4`, link and debug flags.
* Using the builtin compiler include reporting, which is `/showIncludes` for
  MSVC and `-MD` otherwise, it automatically detects used includes and rebuilds
  accordingly.
