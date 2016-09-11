#!/usr/bin/env python
# coding: utf-8


import abc


class AbstractRenderer(object):
    """
    描画可能オブジェクトインタフェース
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def render(self):
        pass
