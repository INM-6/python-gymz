# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='gymz',
    version='0.0.1',
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
