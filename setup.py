#!/usr/bin/env python
from __future__ import absolute_import, print_function

from setuptools import setup, find_packages

import comp_match

NAME = 'comp-match'
PACKAGES = find_packages(
    exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']
)
PACKAGE_DATA = {
    '': ['resources/*.*']
}
AUTHOR = comp_match.__author__
AUTHOR_EMAIL = comp_match.__author_email__
URL = 'https://github.com/franklingu/comp-match'


REQUIRES = []
with open('requirements.txt', 'r') as ifile:
    for line in ifile:
        REQUIRES.append(line.strip())
VERSION = comp_match.__version__
DESCRIPTION = 'Match company names to underline, stock symbols and more'
KEYWORDS = 'match company name stock'
LONG_DESC = comp_match.__doc__

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
