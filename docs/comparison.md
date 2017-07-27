---
layout: default
title: Compare
---

# Performance

A more detailed performance analysis is in the works. Here are just two
provisional data points – note that <span style="color: red;">**this is 
incomplete**</span>. I just created a build-script using Cook for another 
build-system, called [Ninja](https://github.com/ninja-build/ninja), and built 
it using both Cook and Ninja itself. All tests were conducted with a 
best-of-three.

Full build:

```bash
$ time sh -c 'rm -rf build/ && cook > /dev/null'
real	0m7.395s
user	0m18.092s
sys     0m1.300s

$ time sh -c 'rm -rf build/ && ninja > /dev/null'
real	0m7.306s
user	0m17.852s
sys     0m1.272s
```

Incremental build, changing one `.cc` file:

```bash
$ time sh -c 'touch src/state.cc && cook > /dev/null'
real	0m1.764s
user	0m1.592s
sys     0m0.120s

$ time sh -c 'touch src/state.cc && ninja > /dev/null'
real	0m1.531s
user	0m1.348s
sys     0m0.136s
```

Null build:

```bash
$ time sh -c 'cook > /dev/null'
real	0m0.266s
user	0m0.236s
sys     0m0.012s

$ time sh -c 'ninja > /dev/null'
real	0m0.009s
user	0m0.000s
sys     0m0.000s
```

# Some Arguments

Here is just a list of positive and negative aspects at the moment. It will be 
expanded soon, giving more details about each point.

|<span style="color:green">Positive</span>|<span style="color:red">Negative</span>|
|---|---|
|Simple|Not the best IDE support|
|Powerful|Unknown outputs are not possible|
|Extendable|Turing-Complete, no static verification|
|Truly Cross-Platform|No remote cache|
|Fast & Parallel|Not the fastest|
|Correct (also tracks implicit headers)|Does not detect dependencies automatically|
|Multi-Purpose|Dependencies are not verified|
|Flexible Frontend|Uses exact timestamps, not checksum|
|Basic IDE support|No configuration / build split|
|Python, not another DSL|Path handling (improvements?)|
|Handles compiler warnings||
|Depend on arbitrary Python data||
|Post-build dependencies||
|Scalable||
|Incremental||
|Source-Generation||
