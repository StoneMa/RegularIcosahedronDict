#!/usr/bin/env python
# coding: utf-8

import numpy as np
from src.util.debug_util import assert_type_in_container


class BaseShapeMap(object):
    DATA_FORMAT = {'float': 'f',
                   'double': 'd',
                   'int': 'i'}

    def __init__(self, model_id, distance_map, cls, n_div):
        """

        :type distance_map: list(list or np.ndarray)
        :param distance_map: 3Dモデルの重心Gと、Gとグリッド頂点を結ぶ線分とモデルの交点Pの
                             距離情報を含むマップ

        :type cls: int or long
        :param cls: クラスラベル

        :type n_div: int or long
        :param n_div: 分割数

        """
        assert isinstance(model_id, (int, long))
        assert isinstance(cls, (int, long))
        assert isinstance(n_div, (int, long))
        try:
            assert isinstance(distance_map, (list, tuple))
            assert_type_in_container(distance_map, (list, tuple))
        except AssertionError:
            assert isinstance(distance_map, np.ndarray)
            assert distance_map.ndim == 2

        self.model_id = model_id
        self.distance_map = distance_map
        self.cls = cls
        self.n_div = n_div

    def save(self, shp_path, type_name='float'):
        """

        形状マップを.shpファイル形式で保存する

        :type shp_path: str
        :param shp_path: .shpファイルパス

        :type data_id: str
        :param data_id: 個々の形状データに付与されるID

        :type type_name: str
        :param type_name: データ部の型

        """
        raise NotImplementedError

    def __str__(self):
        s = super(BaseShapeMap, self).__str__() + \
            "\n( Model-ID : {}, n-div : {} )\n".format(self.model_id,
                                                       self.n_div)
        for distance_row in self.distance_map:
            s += "[ "
            for distance in distance_row:
                s += "{} ".format(distance)
            s += "]\n"
        return s
