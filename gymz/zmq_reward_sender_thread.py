# -*- coding: utf-8 -*-

import threading
import time
import zmq

from . import misc


class ZMQRewardSenderThread(threading.Thread):
    """Sends rewards via zmq sockets."""

    def __init__(self, thread_id, thread_name, reward_buffer, done_buffer, config, exit_event):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = thread_name
        self._buffer = reward_buffer
        self.done_buffer = done_buffer
        self.exit_event = exit_event
        self._socket = config['RewardSender']['socket']
        self._update_inteval = config['RewardSender']['update_interval']
        self._init_zmq_sockets()

    def _init_zmq_sockets(self):
        """Initializes and binds all zmq sockets"""
        self.context = zmq.Context()

        # Socket to send output
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind('tcp://*:{socket}'.format(socket=self._socket))

    def _send(self):
        """Sends the output buffer"""
        ts = time.time()
        for item in self._buffer[0]:
            item.update({'ts': ts})
        self.socket.send_json(self._buffer[0])

    def run(self):
        while not self.exit_event.is_set():
            t_start = time.time()
            self._send()
            misc.sleep_remaining(t_start, self._update_inteval, 'RewardSenderThread: sleep time negative')
        print '[INFO] RewardSenderThread shutting down.'

    def done(self):
        return self.done_buffer[0]
