#!/usr/bin/env python3

"""This is a **proof-of-concept** VSCode project generator."""

import json
import os
import platform
import subprocess
from collections import defaultdict

subprocess.check_call(['cook', '--results'])

with open('results.json') as file:
    content = json.load(file)

VSCODE = '.vscode'
PROPS = os.path.join(VSCODE, 'c_cpp_properties.json')
TASKS = os.path.join(VSCODE, 'tasks.json')
LAUNCH = os.path.join(VSCODE, 'launch.json')

try:
    os.mkdir(VSCODE)
except:
    pass


def ddd():
    return defaultdict(ddd)


props = defaultdict(ddd)
props['version'] = 3
confs = props['configurations'] = []
default = defaultdict(ddd)
confs.append(default)
default['name'] = 'Default'
defines = default['defines'] = set()
includes = default['includePath'] = set()
path = default['browse']['path'] = set()

for primary, result in content.items():
    if result.get('type') == 'cpp.object':
        defines.update(result['define'].keys())
        includes.update(result['include'])
        path.update(result['include'])

with open(PROPS, 'w') as f:
    json.dump(props, f, default=list, indent=4)

with open(TASKS, 'w') as f:
    json.dump({
        "version": "2.0.0",
        "tasks": [
            {
                "label": "build",
                "type": "shell",
                "command": "python3 vscode.py && cook",
                "args": [],
                "group": "build",
                "presentation": {
                    "reveal": "silent"
                },
                "problemMatcher": []
            }
        ]
    }, f, indent=4)

with open(LAUNCH, 'w') as f:
    json.dump({
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Launch",
                "type": "cppvsdbg" if platform.system() == 'Windows' else 'cppdbg',
                "request": "launch",
                "program": "${workspaceFolder}/build/main",
                "args": [],
                "stopAtEntry": False,
                "cwd": "${workspaceFolder}",
                "environment": [],
                "externalConsole": False,
                "MIMode": "gdb",
                "setupCommands": [
                    {
                        "description": "Enable pretty-printing for gdb",
                        "text": "-enable-pretty-printing",
                        "ignoreFailures": True
                    }
                ],
                "preLaunchTask": "build"
            }
        ]
    }, f, indent=4)
