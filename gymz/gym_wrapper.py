# -*- coding: utf-8 -*-

import numpy as np
import os
import time
import warnings

import gym  # openai gym
import gym.spaces
import gym.wrappers

from .wrapper_base import WrapperBase
from . import messages


class GymWrapper(WrapperBase):
    """Wrapper for the OpenAI Gym toolkit"""

    def __init__(self, config):
        WrapperBase.__init__(self)

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
        self._inter_trial_observation = config['Env']['inter_trial_observation']
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
        self._env.seed(seed)

    def load_env(self, env, *args, **kwargs):
        if 'monitor_args' in kwargs:  # handle monitor args separately
            monitor_args = kwargs['monitor_args']
            del kwargs['monitor_args']

            if not self._monitor and len(monitor_args) > 0:
                warnings.warn('Monitoring not enabled but passing monitor arguments.', RuntimeWarning)

        self._env = gym.make(env, *args, **kwargs)
        self._check_parameters()

        if self._monitor:
            self._env = gym.wrappers.Monitor(self._env, self._monitor_dir, **monitor_args)

    def _check_parameters(self):
        if self._min_reward is not None and np.shape(self._min_reward) != ():
            raise ValueError('min_reward needs to be one dimensional. Please adjust your config.')
        if self._max_reward is not None and np.shape(self._max_reward) != ():
            raise ValueError('max_reward needs to be one dimensional. Please adjust your config.')
        if self._initial_reward is not None and np.shape(self._initial_reward) != ():
            raise ValueError('initial_reward needs to be one dimensional. Please adjust your config.')
        if self._final_reward is not None and np.shape(self._final_reward) != ():
            raise ValueError('final_reward needs to be one dimensional. Please adjust your config.')
        if self._final_reward_null is not None and np.shape(self._final_reward_null) != ():
            raise ValueError('final_reward_null needs to be one dimensional. Please adjust your config.')
        if np.shape(self._inter_trial_observation) != np.shape(self._env.observation_space.sample()):
            raise ValueError('inter_trial_observation is {} dimensional while the obervation space is {} dimensional. These need to be equal. Please adjust your config.'.format(len(np.shape(self._inter_trial_observation)), len(np.shape(self._env.observation_space.sample()))))

    def reset(self):
        self._output = self._env.reset()  # reset returns initial state
        self._done_buffer[0] = False

        # initial reward is always assumed to be zero (by Gym), we
        # allow to overwrite it with a custom value to avoid potential
        # jumps in value from first to second state
        self._reward = self._initial_reward

        self._episode += 1
        self._episode_step = 0
        self._episode_reward = []
        self._episode_observation = []
        self._episode_time_start = time.time()

    def execute_action(self):
        # Gym expects actions in different format depending on type of
        # action space
        if isinstance(self._env.action_space, gym.spaces.Discrete):
            action = self._command_buffer[0][0]['value']
        else:
            action = [self._command_buffer[0][0]['value']]

        self._output, self._reward, self._done_buffer[0], _ = self._env.step(action)

        # record Gym output depending on type of observation space
        if isinstance(self._env.observation_space, gym.spaces.Discrete):
            self._episode_observation.append(self._output)
        elif isinstance(self._env.observation_space, gym.spaces.Box):
            self._episode_observation.append(list(self._output))
        else:
            raise NotImplementedError('Observation space {obs} not supported.'.format(obs=self._env.observation_space))

        self._episode_step += 1

        # in case user provides a reward value, overwrite the one retrieved from Gym
        if self._done_buffer[0] is True:
            if self._final_reward is not None:
                self._reward = self._final_reward
            elif abs(self._reward) < 1e-10:
                self._reward = self._final_reward_null

        self._episode_reward.append(self._reward)

        if self._render:
            self._env.render()

    def update_output_buffer(self):
        assert(self._output_buffer is not None)

        # handle Gym output depending on type of observation space
        if isinstance(self._env.observation_space, gym.spaces.Discrete):
            self._output_buffer[0] = messages.to_message(0, self._env.observation_space.n - 1, self._output)
        elif isinstance(self._env.observation_space, gym.spaces.Box):
            self._output_buffer[0] = messages.to_message(self._env.observation_space.low, self._env.observation_space.high, self._output)
        else:
            raise NotImplementedError('Observation space {obs} not supported.'.format(obs=self._env.observation_space))

    def get_command_buffer(self):
        if self._command_buffer is None:
            # set up buffer depending on type of action space
            if isinstance(self._env.action_space, gym.spaces.Discrete):
                self._command_buffer = [messages.to_message(0, self._env.action_space.n - 1, 0)]
            elif isinstance(self._env.action_space, gym.spaces.Box) and len(self._env.action_space.shape) == 1:
                self._command_buffer = [messages.to_message(self._env.action_space.low, self._env.action_space.high, 0.)]
            else:
                raise NotImplementedError('Action space {acts} not supported.'.format(acts=self._env.action_space))
        return self._command_buffer

    def get_output_buffer(self):
        if self._output_buffer is None:
            self._output_buffer = [[]]
            self._output = self._env.reset()  # reset returns initial observation
            self.update_output_buffer()
        return self._output_buffer

    def clear_output_buffer(self):
        assert(self._output_buffer is not None)

        if isinstance(self._env.observation_space, gym.spaces.Discrete):
            self._output_buffer[0] = messages.to_message(0, self._env.observation_space.n - 1, self._inter_trial_observation)
        elif isinstance(self._env.observation_space, gym.spaces.Box) and len(self._env.observation_space.shape) == 1:
            if np.shape(self._env.observation_space.low) != np.shape(self._inter_trial_observation):
                raise ValueError('Dimensions of inter_trial_observation do not match environment.')
            self._output_buffer[0] = messages.to_message(self._env.observation_space.low, self._env.observation_space.high, self._inter_trial_observation)
        else:
            raise NotImplementedError('Observation space {obs} not supported.'.format(obs=self._env.observation_space))

    def report(self):
        return {
            self._episode: {
                'reward': self._episode_reward,
                'obervation': self._episode_observation,
                'duration': time.time() - self._episode_time_start
            }
        }
