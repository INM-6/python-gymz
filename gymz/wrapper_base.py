# -*- coding: utf-8 -*-

from . import messages


class WrapperBase(object):
    """Base class for all wrappers"""

    def __init__(self):
        self._command_buffer = None
        self._output_buffer = None
        self._reward_buffer = None
        self._done_buffer = None

        self._gym = None
        self._output = None

        self._reward = None
        self._initial_reward = None
        self._min_reward = None
        self._max_reward = None

        self._inter_trial_observation = None

    def done(self):
        return self._done_buffer[0]

    def seed(self, seed):
        """Sets random seed of environment."""
        raise NotImplementedError()

    def load_env(self, env, *args, **kwargs):
        """Loads a specified environment."""
        raise NotImplementedError()

    def reset(self):
        """Resets environment to initial state."""
        raise NotImplementedError()

    def execute_action(self):
        """Executes a single action in an environment."""
        raise NotImplementedError()

    def update_output_buffer(self, data):
        """Updates output buffer with current observation."""
        raise NotImplementedError()

    def update_reward_buffer(self):
        """Updates reward buffer with current reward."""
        assert(self._reward_buffer is not None)
        self._reward_buffer[0] = messages.to_message(self._min_reward, self._max_reward, self._reward)

    def get_command_buffer(self):
        """Initializes command buffer."""
        raise NotImplementedError()

    def get_done_buffer(self):
        """Initializes buffer to signal end of episode."""
        if self._done_buffer is None:
            self._done_buffer = [False]
        return self._done_buffer

    def get_output_buffer(self):
        """Initializes output buffer."""
        raise NotImplementedError()

    def get_reward_buffer(self):
        """Initializes reward buffer."""
        if self._reward_buffer is None:
            self._reward_buffer = [messages.to_message(self._min_reward, self._max_reward, self._initial_reward)]
        return self._reward_buffer

    def clear_output_buffer(self):
        """Replaces observations in output buffer with user defined values."""
        raise NotImplementedError()

    def clear_reward_buffer(self):
        """Replaces reward in reward buffer with user defined values."""
        self._reward_buffer[0] = messages.to_message(self._min_reward, self._max_reward, self._initial_reward)

    def report(self):
        """Writes a custom report."""
        raise NotImplementedError()
