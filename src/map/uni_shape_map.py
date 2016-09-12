#!/usr/bin/env python
# coding: utf-8

import struct
from base_shape_map import BaseShapeMap
from src.obj.grid.triangle_grid import BaseFace


class UniShapeMap(BaseShapeMap):
    def __init__(self, map_id, distance_map, cls, n_div, face_id,
                 traverse_direction):
        """

        :type distance_map: list(list or np.ndarray)
        :param distance_map: 3Dモデルの重心Gと、Gとグリッド頂点を結ぶ線分とモデルの交点Pの
                             距離情報を含むマップ

        :type cls: int or long
        :param cls: クラスラベル

        :type n_div: int or long
        :param n_div: 分割数

        :type face_id: int or long
        :param face_id: 面ID

        :type traverse_direction: BaseFace.UNI_SCAN_DIRECTION
        :param traverse_direction: 面を走査する方向

        """

        super(UniShapeMap, self).__init__(map_id, distance_map, cls, n_div)
        assert isinstance(face_id, (int, long))
        assert isinstance(traverse_direction, BaseFace.UNI_SCAN_DIRECTION)
        self.face_id = face_id
        self.traverse_direction = traverse_direction

    def save(self, shp_path, type_name='float'):
        """

        形状マップを.shpファイル形式で保存する

        :type shp_path: str
        :param shp_path: .shpファイルパス

        :type type_name: str
        :param type_name: データ部の型

        """

        # データ値をバイナリ保存する時のフォーマット
        data_format = BaseShapeMap.DATA_FORMAT[type_name]

        lines = []

        with open(shp_path, mode='wb') as f:

            # .shpファイルであることを示す接頭辞
            lines.append("#SHP\n")
            # ID
            lines.append("#ID\n{}\n".format(self.map_id))
            # クラス情報
            lines.append("#CLASS\n{}\n".format(self.cls))
            # FaceID
            lines.append("#FACE_ID\n{}\n".format(self.face_id))
            # 走査方向
            lines.append(
                "#DIRECTION\n{}\n".format(self.traverse_direction.name))
            # 分割数
            lines.append("#N_DIV\n{}\n".format(self.n_div))
            # マップ型
            lines.append("#TYPE\n{}\n".format(type_name))

            lines.append("#DATA\n")

            f.writelines(lines)

            # データ部の書き込み
            for row in self.distance_map:
                for elem in row:
                    f.write(struct.pack(data_format, elem))
