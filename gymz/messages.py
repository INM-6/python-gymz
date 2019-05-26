# -*- coding: utf-8 -*-

import numpy as np


def to_message(low, high, value):
    assert(np.shape(low) == np.shape(high) == np.shape(value))

    try:

        # convert numpy arrays to lists as they can not be json serialized
        try:
            low = low.tolist()
            high = high.tolist()
            value = value.tolist()
        except:
            pass

        return [{'min': low[i], 'max': high[i], 'value': value[i]} for i in range(len(low))]

    except TypeError:

        # convert numpy types to native types as they can not be json
        # serialized
        try:
            low = low.item()
        except:
            pass

        try:
            high = high.item()
        except:
            pass

        try:
            value = value.item()
        except:
            pass

        return [{'min': low, 'max': high, 'value': value}]
