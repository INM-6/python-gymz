# -*- coding: utf-8 -*-
import re
from setuptools import setup

# determine version from __init__.py without importing it
with open('./gymz/__init__.py', 'r') as f:
    for l in f:
        if '__version__' in l:
            try:
                version = re.compile('[0-9]+.[0-9]+.[0-9]+').search(l).group()
            except AttributeError:
                raise ValueError('Could not determine package version.')
            else:
                break

setup(
    name='gymz',
    version=version,
    author='Jakob Jordan, Philipp Weidel',
    author_email='j.jordan@fz-juelich.de',
    description=('A light-weight ZeroMQ wrapper for the OpenAI Gym.'),
    license='MIT',
    keywords='openai-gym reinforcement-learning zeromq zmq',
    url='https://github.com/INM-6/python-gymz',
    packages=['gymz'],
    package_data={
        'gymz': ['DefaultConfig.json']
    },
    scripts=['gymz-controller'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
    ],
    install_requires=[
        'docopt',
        'gym>=0.8.1',
        'numpy',
        'pyzmq',
    ]
)
