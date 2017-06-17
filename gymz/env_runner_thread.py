# -*- coding: utf-8 -*-

import json
import os
import threading
import time
import warnings

from . import misc


class EnvRunnerThread(threading.Thread):
    """Runs the environment."""

    def __init__(self, thread_id, thread_name, emu, command_buffer, output_buffer, reward_buffer, config, exit_event):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = thread_name
        self.emu = emu
        self.command_buffer = command_buffer
        self.output_buffer = output_buffer
        self.reward_buffer = reward_buffer
        self.exit_event = exit_event
        self._update_interval = config['EnvRunner']['update_interval']  # (s), update interval of ZMQ sockets
        self._inter_trial_duration = config['EnvRunner']['inter_trial_duration']  # (s), duration of no input/no reward state after reset of environment
        self._write_report = config['All']['write_report']
        if self._write_report:
            self._report_file = os.path.join(config['All']['prefix'], config['All']['report_file'])
            self._flush_report_interval = config['All']['flush_report_interval']

            if os.path.isfile(self._report_file):  # file already exists
                if config['All']['overwrite_files']:
                    warnings.warn('Report file already exists. Truncating.', RuntimeWarning)
                    with open(self._report_file, 'w') as f:  # clear file
                        json.dump({}, f)
                else:
                    raise IOError('Report file already exists. Exiting.')
        else:
            self._report_file = None

    def _report(self):
        if not self._write_report:
            return

        try:
            with open(self._report_file, 'r') as f:
                report = json.load(f)
        except IOError:
            report = {}

        report.update(self.emu.report())
        with open(self._report_file, 'w') as f:
            json.dump(report, f)

    def run(self):
        # Reset environment
        self.emu.reset()

        # Run environment
        step = 0
        while not self.exit_event.is_set():
            t_start = time.time()

            if self.emu.done():
                print '[info] EnvRunnerThread: reset'
                t_start_done = time.time()

                if self._write_report and self._flush_report_interval is None:
                    self._report()

                # reset environment
                self.emu.reset()

                # clear all input for a certain duration
                self.emu.clear_output_buffer()
                self.emu.clear_reward_buffer()
                misc.sleep_remaining(t_start_done, self._inter_trial_duration,
                                     'EnvRunnerThread: inter trial sleep time negative')
                t_start = time.time()

                # update buffers to reflect initial state of env
                self.emu.update_output_buffer()
                self.emu.update_reward_buffer()
            else:
                self.emu.execute_action()
                self.emu.update_output_buffer()
                self.emu.update_reward_buffer()

            step += 1

            if self._write_report and self._flush_report_interval is not None and step % self._flush_report_interval == 0:
                self._report()

            misc.sleep_remaining(t_start, self._update_interval,
                                 'EnvRunnerThread: sleep time negative')
        print '[INFO] EnvRunnerThread shutting down.'
