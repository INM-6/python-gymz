# -*- coding: utf-8 -*-

import threading
import time
import zmq

from . import misc


class ZMQObservationSenderThread(threading.Thread):
    """Sends observations via zmq sockets."""
    def __init__(self, thread_id, thread_name, output_buffer, done_buffer, config, exit_event):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = thread_name
        self.output_buffer = output_buffer
        self.done_buffer = done_buffer
        self.exit_event = exit_event
        self._socket = config['ObservationSender']['socket']
        self._update_interval = config['ObservationSender']['update_interval']
        self._init_zmq_sockets()

    def _init_zmq_sockets(self):
        """Initializes and binds all zmq sockets"""
        self.context = zmq.Context()

        # Socket to send output
        self.output_socket = self.context.socket(zmq.PUB)
        self.output_socket.bind('tcp://*:{socket}'.format(socket=self._socket))

    def _send_output(self):
        """Sends the output buffer"""
        ts = time.time()
        for item in self.output_buffer[0]:
            item.update({'ts': ts})
        self.output_socket.send_json(self.output_buffer[0])

    def run(self):
        while not self.exit_event.is_set():
            t_start = time.time()
            self._send_output()
            misc.sleep_remaining(t_start, self._update_interval, 'ObservationSenderThread: sleep time negative')
        print '[INFO] ObservationSenderThread shutting down.'

    def done(self):
        return self.done_buffer[0]
