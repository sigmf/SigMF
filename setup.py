from setuptools import setup

import sigmf


shortdesc = "Signal Metadata Format Specification"
longdesc = """
The Signal Metadata Format (SigMF) specifies a way to describe
sets of recorded digital signal samples with metadata written in JSON.
SigMF can be used to describe general information about a collection
of samples, the characteristics of the system that generated the
samples, and features of the signal itself.

"""

setup(
    name='SigMF',
    version=sigmf.__version__,
    description=shortdesc,
    long_description=longdesc,
    url='https://github.com/gnuradio/SigMF',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=['sigmf'],
    install_requires=['six', 'numpy'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest>3'],
    zip_safe=False
)
