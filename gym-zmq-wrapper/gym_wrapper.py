# -*- coding: utf-8 -*-

import numpy as np
import os
import time

import gym  # openai gym
import gym.spaces
import gym.wrappers

from wrapper_base import WrapperBase


class GymWrapper(WrapperBase):
    """Wrapper for the OpenAI Gym toolkit"""

    def __init__(self, config):
        WrapperBase.__init__(self)

        self._gym = None
        self._output = None

        self._initial_reward = config['Env']['initial_reward']
        try:
            self._final_reward = config['Env']['final_reward']
        except KeyError:
            self._final_reward = None
        try:
            self._final_reward_null = config['Env']['final_reward_null']
        except KeyError:
            self._final_reward_null = None

        self._min_reward = config['Env']['min_reward']
        self._max_reward = config['Env']['max_reward']
        self._render = config['Env']['render']

        self._episode = 0
        self._episode_step = 0
        self._episode_reward = []
        self._episode_observation = []
        self._episode_time_start = time.time()

        self._monitor = config['Env']['monitor']
        if self._monitor:
            self._monitor_dir = os.path.join(config['All']['prefix'], config['Env']['monitor_dir'])

    def seed(self, seed):
        self._gym.seed(seed)

    def load_env(self, env, monitor_args, *args, **kwargs):
        self._gym = gym.make(env, *args, **kwargs)
        if self._monitor:
            self._gym = gym.wrappers.Monitor(self._gym, self._monitor_dir, **monitor_args)

    def reset(self):
        self._output = self._gym.reset()  # reset returns initial state
        self._reward = self._initial_reward  # initial reward is assumed to be zero (by Gym)
        self._done_buffer[0] = False

        self._episode += 1
        self._episode_step = 0
        self._episode_reward = []
        self._episode_observation = []
        self._episode_time_start = time.time()

    def execute_action(self):
        action_space = self._gym.action_space
        if isinstance(action_space, gym.spaces.Discrete):
            action = self._command_buffer[0][0]['value']
        else:
            action = [self._command_buffer[0][0]['value']]

        self._output, self._reward, self._done_buffer[0], _ = self._gym.step(action)

        if isinstance(self._gym.observation_space, gym.spaces.Discrete):
            self._episode_observation.append(self._output)
        elif isinstance(self._gym.observation_space, gym.spaces.Box):
            self._episode_observation.append(list(self._output))
        else:
            raise NotImplementedError('execute_action')

        self._episode_step += 1

        if self._done_buffer[0] is True:
            if self._final_reward is not None:
                self._reward = self._final_reward
            elif abs(self._reward) < 1e-10:
                self._reward = self._final_reward_null

        self._episode_reward.append(self._reward)

        if self._render:
            self._gym.render()

        print action, '->', self._output, self._reward, self._done_buffer[0]

    def update_reward_buffer(self):
        assert(self._reward_buffer is not None)
        self._reward_buffer[0] = [{'min': self._min_reward, 'max': self._max_reward, 'value': self._reward}]

    def update_output_buffer(self):
        assert(self._output_buffer is not None)
        if isinstance(self._gym.observation_space, gym.spaces.Discrete):
            assert(not isinstance(self._output, (list, tuple, np.ndarray))), 'blasdasdghrghgh'
            self._output_buffer[0] = [{'min': 0, 'max': self._gym.observation_space.n - 1, 'value': self._output}]
        elif isinstance(self._gym.observation_space, gym.spaces.Box):
            self._output_buffer[0] = [{'min': self._gym.observation_space.low[i], 'max': self._gym.observation_space.high[i], 'value': self._output[i]} for i in xrange(self._gym.observation_space.shape[0])]
        else:
            raise NotImplementedError('update_output_buffer')

    def get_command_buffer(self):
        action_space = self._gym.action_space
        if self._command_buffer is None:
            if isinstance(action_space, gym.spaces.Discrete):
                self._command_buffer = [[{'value': 0}]]
            elif isinstance(action_space, gym.spaces.Box):
                self._command_buffer = [[]]
                assert(len(action_space.shape) == 1), 'Not implemented for multiple dimensions.'
                for i in xrange(action_space.shape[0]):
                    self._command_buffer[0].append({'value': 0.})
            else:
                raise NotImplementedError('Unknown action space.')
        return self._command_buffer

    def get_output_buffer(self):
        observation_space = self._gym.observation_space
        if self._output_buffer is None:
            if isinstance(observation_space, gym.spaces.Discrete):
                self._output_buffer = [[{'min': 0, 'max': observation_space.n - 1, 'value': 0}]]
            elif isinstance(observation_space, gym.spaces.Box):
                assert(len(observation_space.shape) == 1), 'Not implemented for multiple dimensions.'
                self._output_buffer = [[{'min': self._gym.observation_space.low[i], 'max': self._gym.observation_space.high[i], 'value': 0.} for i in xrange(self._gym.observation_space.shape[0])]]
            else:
                raise NotImplementedError('Unknown observation space.')
        return self._output_buffer

    def get_reward_buffer(self):
        if self._reward_buffer is None:
            self._reward_buffer = [[{'min': self._min_reward, 'max': self._max_reward, 'value': self._initial_reward}]]
        return self._reward_buffer

    def clear_output_buffer(self):
        assert(self._output_buffer is not None)
        if isinstance(self._gym.observation_space, gym.spaces.Discrete):
            self._output_buffer[0] = [{'min': 0, 'max': self._gym.observation_space.n - 1, 'value': 5000}]
        elif isinstance(self._gym.observation_space, gym.spaces.Box):
            self._output_buffer[0] = [{'min': self._gym.observation_space.low[i], 'max': self._gym.observation_space.high[i], 'value': 5000.} for i in xrange(self._gym.observation_space.shape[0])]
        else:
            raise NotImplementedError('clear_output_buffer')

    def clear_reward_buffer(self):
        self._reward_buffer[0] = [{'min': self._min_reward, 'max': self._max_reward, 'value': self._initial_reward}]

    def report(self):
        return {
            self._episode: {
                'reward': self._episode_reward,
                'obervation': self._episode_observation,
                'duration': time.time() - self._episode_time_start
            }
        }
