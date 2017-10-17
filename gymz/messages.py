# -*- coding: utf-8 -*-

import numpy as np


def to_message(low, high, value):
    assert(np.shape(low) == np.shape(high) == np.shape(value))
    try:
        return [{'min': low[i], 'max': high[i], 'value': value[i]} for i in range(len(low))]
    except TypeError:
        return [{'min': low, 'max': high, 'value': value}]
