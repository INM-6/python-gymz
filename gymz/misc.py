# -*- coding: utf-8 -*-

import collections
import json
import logging
import os
import sys
import time


def read_default_config():
    """Reads the default configuration file"""
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'DefaultConfig.json'), 'r') as f:
        return json.load(f)


def recursively_update_dict(d, u):
    """Updates dict d with dict u recursively."""
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = recursively_update_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def sleep_remaining(t_start, t_total, msg='', logger=None):
    """Sleeps the remaining time from now to t_start + t_total."""
    t_end = time.time()
    if t_total > (t_end - t_start):
        time.sleep(t_total - (t_end - t_start))
    else:
        if logger:
            logger.warn(msg)
        else:
            logging.warn(msg)


class SignalHandler(object):
    """
    Handles SIGINT by setting exit event and waiting for threads to
    finish.
    See https://christopherdavis.me/blog/threading-basics.html
    """

    def __init__(self, exit_event, threads):
        self.exit_event = exit_event
        self.threads = threads

    def __call__(self, signum, frame):
        # Set exit event for all threads
        self.exit_event.set()

        # Wait for all threads to finish
        for thread in self.threads:
            thread.join()

        # Shutdown logging
        logging.shutdown()

        # And exit the program
        sys.exit(0)
