#!/usr/bin/env python
# coding: utf-8

import pickle


def save_cache(path, key, value):
    cache = load_cache_dict(path)
    cache[key] = value
    with open(path, 'wb') as f:
        pickle.dump(cache, f)


def load_cache(path, key):
    try:
        return load_cache_dict(path)[key]
    except KeyError:
        return None


def load_cache_dict(path):
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except EOFError:
        return {}
    except IOError:
        return {}
