gymz
====

|Python2.7| |License|

gymz provides a light-weight wrapper for the `OpenAI Gym <https://gym.openai.com/>`__ to allow interaction with reinforcement-learning environments via `ZeroMQ <http://zeromq.org/>`__ sockets.

The wrapper consists of four different threads that coordinate

1. performing steps in an environment
2. receiving actions via a ZeroMQ SUB socket
3. publishing observations via a ZeroMQ PUB socket
4. publishing rewards via a ZeroMQ PUB socket

It was initially designed to be used in combination with `MUSIC <https://github.com/incf-music>`__ enabling online interaction between reinforcement learning environments from the OpenAI Gym and neuronal network models in simulators like `NEST <http://nest-simulator.org/>`__ or `NEURON <http://www.neuron.yale.edu/neuron/>`__.

Installing gymz
---------------

gymz is available via pip:

.. code:: bash

    pip install gymz

Quickstart
----------

An example client is provided (``examples/random_gymz_client.py``) that connects to a running instance of the wrapper, sends random actions and prints observations and rewards received from the environment to the screen. From a terminal start the wrapper with the default configuration file:

.. code:: bash

    gymz-controller gym DefaultConfig.json

and the ``MountainCar-v0`` environment should be rendered on the screen. Afterwards start the client with:

.. code:: bash

    python random_gymz_client.py

The client should now continously print commands, observations and rewards to the terminal. If it does not, please report the issue.

Code status
-----------

gymz is in a fairly early development stage and should be used with care. Please report any unexpected behaviour you encounter and do not hesitate to create PRs.

.. |Python2.7| image:: https://img.shields.io/badge/python-2.7-blue.svg
   :target: https://www.python.org/
.. |License| image:: http://img.shields.io/:license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
