# -*- coding: utf-8 -*-

import scipy.stats
import time
import zmq


# Assault-v0
# command_space = scipy.stats.randint(0, 6)

# Pendulum-v0
# command_space = scipy.stats.uniform(-2, 4)

# FrozenLake-v0
# command_space = scipy.stats.randint(0, 4)

# MountainCar-v0
command_space = scipy.stats.randint(0, 3)

# Initialize and bind zmq sockets
context = zmq.Context()
command_socket = context.socket(zmq.PUB)
command_socket.bind('tcp://*:5555')
output_socket = context.socket(zmq.SUB)
output_socket.connect('tcp://localhost:5556')
output_socket.setsockopt(zmq.SUBSCRIBE, b'')
reward_socket = context.socket(zmq.SUB)
reward_socket.connect('tcp://localhost:5557')
reward_socket.setsockopt(zmq.SUBSCRIBE, b'')

while True:
    time.sleep(0.01)
    # Send a random command
    command = command_space.rvs()
    command_socket.send_json([{'value': command, 'ts': time.time()}])
    print('command', command)

    # Receive output
    output = output_socket.recv_json()
    print('output', output)

    # Receive reward
    reward = reward_socket.recv_json()
    print('reward', reward)
