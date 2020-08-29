from setuptools import setup
import os

shortdesc = "Signal Metadata Format Specification"
longdesc = """
The Signal Metadata Format (SigMF) specifies a way to describe
sets of recorded digital signal samples with metadata written in JSON.
SigMF can be used to describe general information about a collection
of samples, the characteristics of the system that generated the
samples, and features of the signal itself.
"""

# exec version.py to get __version__ (version.py is the single source of the version)
version_file = os.path.join(os.path.dirname(__file__), 'sigmf', 'version.py')
exec(open(version_file).read())

setup(
    name='SigMF',
    version=__version__,
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
    package_data = {'sigmf': ['*.json']},
    install_requires=['six', 'numpy'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest>3'],
    zip_safe=False
)
