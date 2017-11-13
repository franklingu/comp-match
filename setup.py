#!/usr/bin/env python
from __future__ import absolute_import, print_function

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from src import matchers

NAME = 'comp-match'
PACKAGES = [
    'matchers',
]
PACKAGE_DATA = {
    'matchers': ['resources/*.json']
}
AUTHOR = matchers.__author__
AUTHOR_EMAIL = matchers.__author_email__
URL = 'https://github.com/franklingu/comp-match'


REQUIRES = []
with open('requirements.txt', 'r') as ifile:
    for line in ifile:
        REQUIRES.append(line.strip())
VERSION = matchers.__version__
DESCRIPTION = 'Match company names to underline, stock symbols and more'
KEYWORDS = 'match company name stock'
LONG_DESC = matchers.__doc__

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    url=URL,
    keywords=KEYWORDS,
    license='MIT',
    package_dir={'': 'src'},
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    include_package_data=True,
    install_requires=REQUIRES,
    python_requires='>=3.5, <4',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
)
