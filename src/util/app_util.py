#!/usr/bin/env python
# coding: utf-8

import pickle


def save_cache(path, key, value):
    """

    引数にとった値をキャッシュとして保存する

    :type path: str
    :param path: キャッシュ保存パス

    :type key: str
    :param key: データと対応付けるキー

    :type key: str
    :param value: キャッシュとして保存するデータ

    """
    cache = load_cache_dict(path)
    cache[key] = value
    with open(path, 'wb') as f:
        pickle.dump(cache, f)


def load_cache(path, key):
    """

    保存したキャッシュデータを取り出す


    :type path: str
    :param path: キャッシュ保存パス

    :type key: str
    :param key: 取り出したいデータに対応付けされたキー

    :rtype: T
    :return: keyと対応付けされたデータ

    """
    try:
        return load_cache_dict(path)[key]
    except KeyError:
        return None


def load_cache_dict(path):
    """

    キャッシュデータをまとめた辞書を取得する

    :type path: str
    :param path: 辞書保存パス

    :rtype: dict
    :return: キャッシュデータをまとめた辞書

    """
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except EOFError:
        return {}
    except IOError:
        return {}
