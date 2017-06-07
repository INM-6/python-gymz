# -*- coding: utf-8 -*-

import collections
import sys
import time


def recursively_update_dict(d, u):
    """Updates dict d with dict u recursively."""
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = recursively_update_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def sleep_remaining(t_start, t_total, msg=''):
    t_end = time.time()
    if t_total > (t_end - t_start):
        time.sleep(t_total - (t_end - t_start))
    else:
        print msg


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

        # And exit the program
        sys.exit(0)
