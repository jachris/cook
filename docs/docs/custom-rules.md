---
layout: docs
title: Custom Rules
---

# Custom Rules

## Introduction

Writing a custom rule is very easy with Cook. Just like the whole system,
rules are being written in the Python programming language. Don't worry if you
do not know Python ‒ you should still be able to write basic rules very
quickly.

A rule is technically a Python generator, which means that it is a function
whose execution can be stopped and resumed at any point by using the `yield` 
statement. Unlike other build-systems, looking at the rule definition does
not automatically give you information about things like output files or 
commands used to build them. This is because rules in Cook are much 
higher-level.

## Phase One (Evaluation)

When building a C++ library for example, one does not specify the command to be
used to build it, but instead it's sources and output "name" ‒ which is 
different from the final output "path" because of platform-specific details.
The rule automatically decides which extension to add and also, which flags
should be used by default without having the user specifying them.

As a result, the rule must be able to perform some computations before it is
known, which files are produced and what their dependencies are. This happens
during the first phase ‒ anything before the first `yield`. A rule should then
use `yield core.publish(...)` to inform the system about it's inputs, outputs
and others.

## Phase Two (Execution)

If the system thinks that it is necessary to redo the task, then the execution
will be resumed when all inputs of the task are done. The rule must now produce
all outputs that it promised to deliver by using `core.publish(outputs=...)`.
The rule should only use files declared in the `inputs` field of the 
publication or arbitrary Python objects (`str`, `dict`, usw.) declared in the
`check` field.

**Optional:** Most rules are done now. However, there are some cases when it is necessary to
add additional inputs **after** execution. For example, a `.cpp` file might
`#include` other `.h` files. The compiler can tell us which files were 
including after building the `.cpp` file. This information can be passed on to
the system by using `yield core.deposit(...)`. Input files as described above
can be passed using the `inputs` keyword argument. However, these input files
may not be files which are outputs of other tasks, because this might lead to
an incorrect build, where one task is done before its dependencies are. 
Additionally, warnings can be added as well by using the `warnings` argument. 
The warnings will be displayed immediately after that and also at the start of 
every build process involving the current task when it is not redone. This 
means that warnings are preserved and that actually are warnings will be 
emitted on every build.

## Example

Let's try to build a simple rule which takes a text file, a dictionary and an
output name. It will replace every occurrence of a key included in the 
dictionary by its associated value. Calling our rule might look like this:

```python
replace(
    source='input.txt',
    destination='output.txt',
    mapping={
        'Bob': 'Alice',
        'Hello': 'Hi',
    }
)
```

This should turn our input file `input.txt` with

```Bob: "Hello, how are you?"```

into `output.txt` with the following contents:

```Alice: "Hi, how are you?"```

We will create a function with the `def` statement and use `@core.rule`, a 
so-called "decorator" to turn the normal function into a rule.

```python
from cookpy import core

@core.rule
def replace(source, destination, mapping):
    ...
```

The `source` parameter will contain the path relative to the current `BUILD.py`
begin executed ‒ because of that, we will use `core.resolve()`. Becase the 
`destination` should be relative to be build directory, `core.build()` is 
applied.

```python
    source = core.resolve(source)
    destination = core.build(destination)
    ...
```

We now know where are source and target files are, so we will pause the 
execution at this point to only continue when we have to rebuild. In addition
to a helpful message, we also pass the `mapping` as to the `check`-parameter.
This is because we want to rebuild whenever the mapping changes.

```python
    yield core.publish(
        inputs=[source],
        message='Processing {}'.format(source),
        outputs=[destination],
        check=mapping
    )
    ...
```

Anything below that `yield` will only be executed if needed, so we will just
continue by writing the code that will turn the keys into their values. In
order to do that, we will first read the input file, then iterate over the 
items of the `mapping` and replace every key with its value. Finally, we write
everything to the output file.

```python
    with open(source) as file:
        content = file.read()
    for key, value in mapping.items():
        content = content.replace(key, value)
    with open(destination, 'w') as file:
        file.write(content)
```

## Result

That's it. Below you can see the whole rule at once.

```python
@core.rule
def replace(source, destination, mapping):
    source = core.resolve(source)
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
```
