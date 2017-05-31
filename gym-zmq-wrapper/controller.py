# -*- coding: utf-8 -*-

"""
Controller.
Start threads for running an environment in an emulator and expose
input/output/reward buffers via ZeroMQ.

Usage:
    controller.py <emu> <config> [--directory <dir>] [--grayscale]
    controller.py -h | --help

Options:
    -h --help         Show this screen
    -d --directory    Directory with roms (required for ALE) [default: ./]
    --grayscale       Convert 2d screens to grayscale to reduce output dimensions [default: False]
"""

import docopt
import json
import os
import signal
import threading
import time

import misc
from zmq_reward_sender_thread import ZMQRewardSenderThread
from zmq_observation_sender_thread import ZMQObservationSenderThread
from zmq_command_receiver_thread import ZMQCommandReceiverThread
from env_runner_thread import EnvRunnerThread
from gym_wrapper import GymWrapper


def run(args):
    # Load default configuration file
    with open('./DefaultConfig.json', 'r') as f:
        config = json.load(f)

    # Parse user config file and update config
    with open(args['<config>'], 'r') as f:
        misc.recursively_update_dict(config, json.load(f))

    # Set prefix
    if config['All']['prefix'] is None:
        config['All']['prefix'] = os.path.split(args['<config>'])[0]

    # Create wrapper instance
    if args['<emu>'] == 'gym':
        emu = GymWrapper(config)
    else:
        raise NotImplementedError('Unknown emulator.')

    # Load an environment
    emu.load_env(config['Env']['env'], config['Env']['monitor_args'])

    if args['--grayscale']:
        # Set grayscale (use only for ATARI environments)
        emu.to_grayscale(True)

    # Fix random seed for reproducibility
    if config['All']['seed'] >= 0:
        emu.seed(config['All']['seed'])

    # Use mutable objects (lists) as containers for buffers to retain
    # correct pointers and avoid globals
    command_buffer = emu.get_command_buffer()
    output_buffer = emu.get_output_buffer()
    reward_buffer = emu.get_reward_buffer()
    done_buffer = emu.get_done_buffer()
    exit_event = threading.Event()

    runner_thread = EnvRunnerThread(0, 'runner_thread', emu, command_buffer, output_buffer, reward_buffer, config, exit_event)
    zmq_reward_sender_thread = ZMQRewardSenderThread(1, 'zmq_reward_sender_thread', reward_buffer, done_buffer, config, exit_event)
    zmq_sender_thread = ZMQObservationSenderThread(2, 'zmq_sender_thread', output_buffer, done_buffer, config, exit_event)
    zmq_receiver_thread = ZMQCommandReceiverThread(3, 'zmq_receiver_thread', command_buffer, done_buffer, config, exit_event)

    # Set up signal handler for SIGINT to let all threads exit
    # gracefully
    signal.signal(signal.SIGINT, misc.SignalHandler(
        exit_event, [runner_thread, zmq_reward_sender_thread, zmq_sender_thread, zmq_receiver_thread]))

    # Fire up the threads, they will not terminate unti SIGINT is received
    runner_thread.start()
    zmq_reward_sender_thread.start()
    zmq_sender_thread.start()
    zmq_receiver_thread.start()

    # Keep main thread alive to be able to receive SIGINT
    while True:
        time.sleep(1000)

if __name__ == '__main__':
    run(docopt.docopt(__doc__))
