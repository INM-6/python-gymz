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
    scripts=['gymz-controller'],
    data_files=[('', ['DefaultConfig.json'])],
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
    ],
)
