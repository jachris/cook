---
layout: docs
title: Correctness
---

# Correctness
{:.no_toc}

* TOC
{:toc}


## Guarantees

The system ensures that a task will be executed if one if the following is true:

- An output does not exist.
- An input-path changed.
- An input-timestamp changed.
- An output-path changed.
- An output-timestamp changed.
- A deposit-timestamp changed.
- The check-object changed.

You are free to use any version control system you like as long as it modifies
timestamps when replacing or patching files. Cook is safer than Make which only
relies on two properties: output-existence and input-timestamps being less than
the output timestamps. For example, make will typically not rebuild if you 
change a command to include a new flag, but Cook would track that flag using
the check-object.

Additionally, since Cook also tracks the output timestamps, you are free to
go into the build directory and edit files at will. The edited files will be
rebuild. All in all, the criteria should be really safe in practice, since 
version control systems like git guarantee that they will set the current time 
as the timestamp on every file they modify. On top of that, Cook will delete 
files in your build directory which are not
mentioned in your build script. This means you really always get a correct 
build. Additional security measures include tracking whether an input changed
during the execution of a rule, since that might violate our correctness 
requirements, and also ensuring that the output was actually at least touched 
by the rule.


## Warnings

Cook will store the warnings your compiler produces. It will remind you of 
these warnings by reprinting them when necessary. This way `-Werror` is not
really needed since it is mostly used to make sure that one does not forget
the warnings when they are not reprinted by Make or other tools.


## Reproducibility

The [builtin rules]({% link docs/rules/index.md %}) provided by Cook are 
designed to output reproducible results. 
[This website](https://reproducible-builds.org/) talks about why this might be 
important for you or users of your software. Performing a build on the same
path and using the same environment (including compiler versions, etc.) as 
someone else should ideally yield bit-by-bit identical results. If you 
encounter a case where this is not true, please 
[file an issue](https://github.com/jachris/cook/issues/new).
