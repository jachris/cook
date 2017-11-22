#!/usr/bin/env python3

"""This is a **proof-of-concept** CLion project generator."""

import functools
import json
import subprocess
import sys

subprocess.check_call(['cook', '--results'])

with open('results.json') as file:
    content = json.load(file)

with open('CMakeLists.txt', 'w') as file:
    w = functools.partial(print, file=file)
    w('cmake_minimum_required(VERSION 2.8.8)')
    w()
    w('add_custom_target(COOK COMMAND ' + sys.executable + ' clion.py COMMAND cook '
      'WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})')
    w()

    outputs = {}
    for primary, result in content.items():
        for output in result['outputs']:
            outputs[output] = primary

    for primary, result in content.items():
        if result.get('type') == 'cpp.object':
            cpp = [file for file in result['inputs'] if file.endswith('.cpp')]
            w('add_library({} OBJECT {})'.format(primary, ' '.join(cpp)))
            defines = ' '.join(name + '=' + str(val) for name, val
                               in result['define'].items())
            if defines:
                w('target_compile_definitions({} PRIVATE {})'
                  .format(primary, defines))
            includes = result['include']
            if includes:
                w('target_include_directories({} PRIVATE {})'.format(
                    primary, ' '.join(includes)
                ))
            w()
