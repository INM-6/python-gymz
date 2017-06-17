# -*- coding: utf-8 -*-


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

    def get_done_buffer(self):
        if self._done_buffer is None:
            self._done_buffer = [False]
        return self._done_buffer

    def get_reward(self):
        return self._reward

    def done(self):
        return self._done_buffer[0]

    def seed(self, seed):
        raise NotImplementedError()

    def load_env(self, env, *args, **kwargs):
        raise NotImplementedError()

    def get_output_dimensions(self, native=False):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError()

    def execute_action(self, action):
        raise NotImplementedError()

    def update_output_buffer(self):
        raise NotImplementedError()

    def get_command_buffer(self):
        raise NotImplementedError()

    def get_output_buffer(self):
        raise NotImplementedError()

    def get_reward_buffer(self):
        raise NotImplementedError()

    def clear_output_buffer(self):
        raise NotImplementedError()

    def clear_reward_buffer(self):
        raise NotImplementedError()

    def report(self):
        raise NotImplementedError()
