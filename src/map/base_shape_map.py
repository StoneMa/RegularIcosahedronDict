#!/usr/bin/env python
# coding: utf-8

import numpy as np
from src.util.debug_util import assert_type_in_container


class BaseShapeMap(object):
    DATA_FORMAT = {'float': 'f',
                   'double': 'd',
                   'int': 'i'}

    def __init__(self, distance_map, cls, n_div):
        try:
            assert isinstance(distance_map, (list, tuple))
            assert_type_in_container(distance_map, (list, tuple))
        except AssertionError:
            assert isinstance(distance_map, np.ndarray)
            assert distance_map.ndim == 2

        self.distance_map = distance_map
        self.cls = cls
        self.n_div = n_div

    def save(self, shp_file_root, data_id, type_name='float'):
        """

        形状マップを.shpファイル形式で保存する

        :type shp_file_root: str
        :param shp_file_root: .shpファイルパス

        :type data_id: str
        :param data_id: 個々の形状データに付与されるID

        :type type_name: str
        :param type_name: データ部の型

        """
        raise NotImplementedError

    def __str__(self):
        s = super(BaseShapeMap, self).__str__() + "(n-div : {}, )"
        for distance_row in self.distance_map:
            for distance in distance_row:
                s += "{}".format(distance)
        return s
