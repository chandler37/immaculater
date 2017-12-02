"""Immaculater CLI setuptools-based setup module."""

import re
from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'todo', 'todo.py')) as f:
    version = re.search(
        r'^__version__\s*=\s*"(.*)"',
        f.read(),
        re.M).group(1)

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='immaculater-cli',

    packages=['todo'],

    version=version,

    description='Immaculater Command-Line Interface',
    long_description=long_description,

    url='https://github.com/chandler37/immaculater',

    author='David L. Chandler',
    author_email='immaculaterhelp@gmail.com',

    license='Apache License 2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='to do todo list command line interface cli',

    py_modules=["todo"],

    install_requires=[
        'python-gflags',
        'requests',
        'six',
    ],

    entry_points={
        'console_scripts': [
            'todo=todo.todo:main',
        ],
    },
)
