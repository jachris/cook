#!/usr/bin/env python3

import setuptools
import os

path = os.path.join(os.path.dirname(__file__), 'cook', 'core', '__init__.py')
with open(path) as file:
    for line in file:
        if line.startswith('version = ('):
            version = '.'.join(line[len('version = ('):-2].split(', '))
            break
    else:
        raise RuntimeError('could not extract version from "{}"'.format(path))

setuptools.setup(
    name='cook',
    version='0.1.0',
    description='desc',
    long_description='long_desc',
    url='https://getcook.org/',
    author='koehlja',
    packages=['cook', 'cook.core'],
    entry_points={
        'console_scripts': ['cook = cook.__main__:main']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers'
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools'
    ],
)
