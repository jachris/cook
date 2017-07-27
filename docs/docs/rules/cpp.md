---
layout: docs
title: C++ Rules
---

# C++ Rules

## Executable

```python
cpp.executable(
    name, sources=None, include=None, define=None, flags=None,
    links=None, compiler=None, warnings_are_errors=False, scan=True
)
```

| Parameter | Description |
|---|---|
|`name`|Name of the output without extension|
|`sources`|List of c++ source files|
|`include`|List of include directories|
|`define`|Dictionary of compiler definitions|
|`flags`|Additional flags to pass to the compiler|
|`links`|List of libraries to link with (`str` or `cpp.*_library`)|
|`compiler`|Path to a compiler|
|`warnings_are_errors`|Compiler warnings are treated as errors|
|`scan`|Automatically track implicit header dependencies (`#include ...`)|


## Static Library

```python
cpp.static_library(
    name=None, sources=None, include=None, define=None, flags=None,
    headers=None, compiler=None, warnings_are_errors=False, scan=True
)
```

| Parameter | Description |
|---|---|
|`name`|Name of the output without extension|
|`sources`|List of c++ source files|
|`include`|List of include directories|
|`define`|Dictionary of compiler definitions|
|`flags`|Additional flags to pass to the compiler|
|`headers`|List of public interface include directories for dependants|
|`compiler`|Path to a compiler|
|`warnings_are_errors`|Compiler warnings are treated as errors|
|`scan`|Automatically track implicit header dependencies (`#include ...`)|


## Shared Library

```python
cpp.shared_library(
    name, sources, include=None, define=None, flags=None, headers=None,
    compiler=None, warnings_are_errors=False, scan=True, msvc_lib=False
)
```

| Parameter | Description |
|---|---|
|`name`|Name of the output without extension|
|`sources`|List of c++ source files|
|`include`|List of include directories|
|`define`|Dictionary of compiler definitions|
|`flags`|Additional flags to pass to the compiler|
|`headers`|List of public interface include directories for dependants|
|`compiler`|Path to a compiler|
|`warnings_are_errors`|Compiler warnings are treated as errors|
|`scan`|Automatically track implicit header dependencies (`#include ...`)|
|`msvc_lib`|Place MSVC import library into build directory instead intermediate|


## Object

```python
cpp.object(
    name=None, sources=None, include=None, define=None, flags=None,
    compiler=None, error_warnings=False, scan=True
)
```

| Parameter | Description |
|---|---|
|`name`|Name of the output without extension|
|`sources`|List of c++ source files|
|`include`|List of include directories|
|`define`|Dictionary of compiler definitions|
|`flags`|Additional flags to pass to the compiler|
|`compiler`|Path to a compiler|
|`warnings_are_errors`|Compiler warnings are treated as errors|
|`scan`|Automatically track implicit header dependencies (`#include ...`)|
