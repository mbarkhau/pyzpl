# -*- coding: utf-8 -*-
# Copyright (c) 2016 Manuel Barkhau <mbarkhau@gmail.com>
# License: MIT (see LICENSE file)
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import io
from setuptools import setup, find_packages

from pyzpl import __version__

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
README_PATH = os.path.join(PROJECT_DIR, 'README.rst')

with io.open(README_PATH, encoding='utf-8') as fh:
    README = fh.read()


setup_requires = [
    # TODO (mb 2016-11-22): implement faster parsing using cython
    # 'cython',
    'flake8',
    'pytest-runner',
]

tests_require = [
    'pytest',
]

install_requires = [
    'six',
]

extras_requires = {
    'build': [
        'wheel',
    ],
    'dev': [
        'ipython',
        'pudb',
    ],
}

setup(
    name='pyzpl',
    version=__version__,
    description=README.splitlines()[0],
    long_description=README,
    keywords="cli zpl zmq serialization",
    url='https://github.com/mbarkhau/pyzpl/',
    author='Manuel Barkhau',
    author_email='mbarkhau@gmail.com',
    license='MIT',
    packages=find_packages(),
    entry_points="""
        [console_scripts]
        zpl=pyzpl:main
    """,
    setup_requires=setup_requires,
    install_requires=install_requires,
    extras_require=extras_requires,
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        'Topic :: Utilities',
    ],
)
