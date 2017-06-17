# -*- coding: utf-8 -*-

import threading
import time
import warnings
import zmq


class ZMQCommandReceiverThread(threading.Thread):
    """Receives command via zmq socket."""

    def __init__(self, thread_id, thread_name, command_buffer, done_buffer, config, exit_event):
        threading.Thread.__init__(self)

        self.thread_id = thread_id
        self.name = thread_name
        self.command_buffer = command_buffer
        self.done_buffer = done_buffer
        self.exit_event = exit_event
        self._socket = config['CommandReceiver']['socket']
        self._time_stamp_tolerance = config['CommandReceiver']['time_stamp_tolerance']
        self._init_zmq_sockets()

    def _init_zmq_sockets(self):
        """Initializes and binds all zmq sockets"""
        self.context = zmq.Context()

        # Socket to receive commands
        self.command_socket = self.context.socket(zmq.SUB)
        self.command_socket.RCVTIMEO = 1000  # set timeout to allow for checking exit event
        self.command_socket.connect('tcp://localhost:{socket}'.format(socket=self._socket))
        self.command_socket.setsockopt(zmq.SUBSCRIBE, "")

    def _recv_command(self):
        """Receives a command via zmq and updates the command buffer"""
        self.command_buffer[0] = self.command_socket.recv_json()
        ts = time.time()
        if abs(ts - self.command_buffer[0][0]['ts']) > self._time_stamp_tolerance:
            warnings.warn('CommandReceiverThread desynchronized.', RuntimeWarning)

    def run(self):
        while not self.exit_event.is_set():
            # use try-except block without timeout defined above to
            # allow thread to exit even if no event is ever received
            try:
                self._recv_command()
            except:
                pass
        print '[INFO] CommandReceiverThread shutting down.'

    def done(self):
        return self.done_buffer[0]
