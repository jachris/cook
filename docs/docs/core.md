---
layout: docs
title: Core Reference
---

# Core Reference
{:.no_toc}

* TOC
{:toc}


The whole API is available inside the `core` subpackage.

```python
from cook import core
```

## core.**absolute()**

```python
core.absolute(path_or_paths)
```

If `path_or_paths` is a single `str`, then its absolute path version will be
returned as a single `str` as well. Otherwise, it will be considered as an
iterable an a `list` with the absolute path of all given paths will be 
returned.


## core.**base_no_ext()**

```python
core.base_no_ext(path)
```

Return the basename of the input `path` without its extension. For example 
`/test/example.png` will return `example`.


## core.**build()**

```python
core.build(path_or_paths)
```

Same `path_or_paths` interpretation as in `core.absolute()`. Will return the
paths relative to the current build directory.


## core.**call()**

```python
core.call(command, cwd=None, env=None)
```

Executes the given `command`, blocking the current thread. If `cwd` is given,
then it wil be executed in that directory, otherwise in the current one. If
the dictionary `env` is given, then the execution will happen inside that
environment, **otherwise the environment will be empty** for reproducibility
reasons. Returns the output of the command.


## core.**CallError**

Exception to be raised when `core.call()` exits with a non-zero value. The
output of the command is available as the instance variable `output`.


## core.**checksum()**

```python
core.checksum(*objects)
```

Calculate an MD5-checksum (128 bits) of the given object. The types of the 
object and sub-objects (in case of containers) may only consist of 

- int
- None
- bool
- str
- bytes, bytearray, ...
- dict, ...
- set, frozenset, ...
- list, tuple, generator, ...

A TypeError will be raised if an unsupported type is encountered. The builtin 
hash-function is different, since it has randomized output for strings, bytes 
and datetime objects and is sometimes even slower. This can be useful if you
want to provide an anonymous version of rules to give outputs a name depending
on other inputs. It is also used internally to process the `check` argument of
`core.publish()`.


## core.**debug|info|warning|error()**

```python
core.debug(*objects, sep=' ')
core.info(*objects, sep=' ')
core.warning(*objects, sep=' ')
core.error(*objects, sep=' ')
```

Emit a log entry on the given level. The `objects` will be transformed to 
`str` and then joined by the separator given by `sep`.


## core.**default()**

```python
core.default(*results)
```

Mark the given tasks as default tasks, which means they will be executed if no
explicit targets are given to the system. If no task is marked as default, then
every task will be build. The `results` are the objects returned by a rule.


## core.**deposit()**

Inform the system of additional inputs after execution.

```python
core.deposit(inputs=None, warnings=None)
```

Some rules need to add more inputs after they have been executed.
A C++ compiler might emit used header files for example. If the
rule deposits these additional paths, then the corresponding files
will be checked for changes in the next build and the rule will be
rebuild if there were any changes.

The 'deposits' must be an iterable which contains relative or
absolute paths, with relative ones being interpreted relative to
the build directory.


## core.**extension()**

```python
core.extension(path)
```

Return the extension of the `path`.


## core.**glob()**

```python
core.glob(pathname)
```

Globs for the `pathname`. The character `?` matches one symbol, `*` matches
any number of all characters excluding `/` (or `\` Windows) and `**` matches
all including the directory separator. The glob is carried out relative to the
currently loaded script.


## core.**intermediate()**

```python
core.intermediate(path_or_paths)
```

Same `path_or_paths` interpretation as in `core.absolute()`. All paths will be
returned relative to the intermediate directory.


## core.**linux**

True if the host is a linux system.


## core.**load()**

```python
core.load(path)
```

Execute the build script given by `path` and return it's global symbols. The
path is interpreted relative to the currently loaded script.


## core.**mac**

True if the host is a mac system.


## core.**option()**

```python
core.option(name, type=bool, default=None, help='')
```

Declare an option with the identifier `name`. The `type` may be one of `str`, 
`int`, `bool` and `float`. The `default` will be returned if no value was given
by the user. You can also specify a `help` message giving more information
about the option. Any option name can only be declared once. If you need an
option in multiple files, you need to either `core.load()` a common file to 
share the option or if one loads the other, then you can access the option if
it is a global symbol.


## core.**publish()**

Informs the system about the task.

```python
core.publish(
    inputs=None, message=None, outputs=None, check=None, force=False, 
    result=None, phony=False
)
```

If 'inputs' is set, it must be an iterable which yields the paths
to the files which will be used by the rule. These paths can be
relative or absolute, with relative ones being interpreted relative
to the build directory.

The 'message' must be a string. It will be displayed if and when the
execution of the rule is resumed after analysis.

The paramter 'outputs' must be set to an iterable and it must
contain at least one path. The rule promises to create these files
if they do not exist and update their timestamps if it is executed.
Paths can be relative or absolute, with relative ones being
interpreted relative to the build directory.

The object passed to 'check' will be used in addition to the normal
procedure to determine whether to rebuild or not. Only types that
can be checksummed are allowed: str, bool, int, float, None, bytes,
bytearray, dict, set, frozenset, list, tuple.

If 'force' is true, the rule is guaranteed to be executed if it is
not excluded by the user.

A rule may publish a 'result', which must be a dict if set. It must
not contain the keys "outputs" and "inputs", since these will be set
by the system. The key "output" will also be set if the rule
produces only one output file. The contents of the resulting
dictionary will be returned as a namespace when calling the rule.

If a rule is declared as 'phony' by setting it to true, it will be
assumed that it does not produce any outputs. The strings passed in
outputs are taken as a name which can be used for example when
defining procedures groups of rules.


## core.**random()**

```python
core.random(suffix='')
```

Returns a a string of 16 random lowercase-alpha-numeric characters followed by
the given `suffix`.


## core.**relative()**

```python
core.relative(path_or_paths)
```

Same `path_or_paths` interpretation as in `core.absolute()`. All paths will be
transformed to relative ones according to the directory where Cook is executed.
This is not the same as `core.source()`.


## core.**rule()**

```python
core.rule(func)
```

Transform the given `func` to a rule. This should be used as a decorator.


## core.**source()**

```python
core.source(path_or_paths)
```

Same `path_or_paths` interpretation as in `core.absolute()`. All paths will be
interpreted relatively to the currently loaded script. This is not the same as
`core.relative()`.


## core.**task()**

```python
core.task(func)
```

Similar to `core.rule`, in that it transforms the `func` to a rule. However,
this rule is immediately called without arguments and the result is returned.
Useful for rules needed only once.


## core.**temporary()**

```python
core.temporary(path_or_paths)
```

Same `path_or_paths` interpretation as in `core.absolute()`. Interpret all
paths relatively to the temporary directory which will be cleaned each time
before starting the evaluation.


## core.**which()**

```python
core.which(file, env=os.environ)
```

Search for an executable named `file` the locations specified by `env['PATH']`.


## core.**windows**

True if the host is a windows system.
