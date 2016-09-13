#!/usr/bin/env python
# coding: utf-8

import os
import struct
from src.obj.grid.base_grid import BaseGrid
from base_shape_map import BaseShapeMap


class BandShapeMap(BaseShapeMap):
    def __init__(self, model_id, distance_map, cls, n_div, band_type):
        """

        :type model_id: int or long:
        :param model_id: 対象3DモデルID

        :type distance_map: list(list or np.ndarray)
        :param distance_map: 3Dモデルの重心Gと、Gとグリッド頂点を結ぶ線分とモデルの交点Pの
                             距離情報を含むマップ

        :type cls: int or long
        :param cls: クラスラベル

        :type n_div: int or long
        :param n_div: 分割数

        :type band_type: BaseGrid.BAND_TYPE
        :param band_type: 帯形状マップのタイプ

        """

        super(BandShapeMap, self).__init__(model_id, distance_map, cls, n_div)
        self.band_type = band_type

    def save(self, shp_path, type_name='float'):

        target_dir = os.path.dirname(shp_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # データ値をバイナリ保存する時のフォーマット
        data_format = BaseShapeMap.DATA_FORMAT[type_name]

        lines = []

        with open(shp_path, mode='wb') as f:

            # .shpファイルであることを示す接頭辞
            lines.append("#SHP\n")
            # ID
            lines.append("#ID\n{}\n".format(self.model_id))
            # クラス情報
            lines.append("#CLASS\n{}\n".format(self.cls))
            # 走査方向
            lines.append("#BAND_TYPE\n{}\n".format(self.band_type.name))
            # 分割数
            lines.append("#N_DIV\n{}\n".format(self.n_div))
            # マップ型
            lines.append("#DATA_TYPE\n{}\n".format(type_name))

            lines.append("#DATA\n")

            f.writelines(lines)

            # データ部の書き込み
            for row in self.distance_map:
                for elem in row:
                    f.write(struct.pack(data_format, elem))
