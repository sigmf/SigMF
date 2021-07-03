#!/usr/bin/env python3
from setuptools import setup
import os
import re

shortdesc = "Signal Metadata Format Specification"
longdesc = """
The Signal Metadata Format (SigMF) specifies a way to describe
sets of recorded digital signal samples with metadata written in JSON.
SigMF can be used to describe general information about a collection
of samples, the characteristics of the system that generated the
samples, and features of the signal itself.
"""

with open(os.path.join('sigmf', '__init__.py')) as handle:
    version = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', handle.read()).group(1)

setup(
    name='SigMF',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    url='https://github.com/gnuradio/SigMF',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points = {
        'console_scripts': ['sigmf_validate=sigmf.validate:main']
    },
    packages=['sigmf'],
    package_data = {
        'sigmf': ['*.json'],
    },
    install_requires=['six', 'numpy', 'pysimplegui==4.0.0'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest>3'],
    zip_safe=False
)
