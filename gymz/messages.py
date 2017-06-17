# -*- coding: utf-8 -*-


def to_message(low, high, value):
    try:
        return [{'min': low[i], 'max': high[i], 'value': value[i]} for i in xrange(len(low))]
    except TypeError:
        return [{'min': low, 'max': high, 'value': value}]
