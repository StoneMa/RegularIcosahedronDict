#!/usr/bin/env python
# coding: utf-8

import os
import struct

import numpy as np

from obj3d import Obj3d
from src.grid.icosahedron_grid import IcosahedronGrid, IcosahedronFace


class ShapeMap(object):
    """

    三次元モデルの重心から表面までの距離を、グリッドの頂点単位で記録するマップのクラス

    """

    DATA_FORMAT = {'float': 'f',
                   'double': 'd',
                   'int': 'i'}

    def __init__(self, face_ids, shape_maps, cls, n_div, traverse_direction):
        """

        :type face_ids: list(int)
        :param face_ids: FaceIDのリスト

        :type shape_maps: list(np.ndarray)
        :param shape_maps: 形状マップのリスト

        :type cls: int
        :param cls: クラスラベル

        :type n_div: int
        :param n_div: 分割数

        :type traverse_direction: IcosahedronGrid.DIRECTION
        :param traverse_direction: 面を走査する方向

        """

        assert len(face_ids) == len(shape_maps)

        self.shape_map_dict = dict(zip(face_ids, shape_maps))

        self.cls = cls
        self.n_div = n_div
        self.traverse_direction = traverse_direction

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

        # 指定したクラスラベル・方向専用のディレクトリを作る
        sub_root = os.path.join(shp_file_root, data_id,
                                self.traverse_direction.name)
        if not os.path.exists(sub_root):
            os.makedirs(sub_root)

        # データ値をバイナリ保存する時のフォーマット
        data_format = ShapeMap.DATA_FORMAT[type_name]

        for face_id, shape_map in self.shape_map_dict.items():

            path = os.path.join(sub_root, "{}.shp".format(face_id))

            lines = []

            with open(path, mode='wb') as f:

                # .shpファイルであることを示す接頭辞
                lines.append("#SHP\n")
                # ID
                lines.append("#ID\n{}\n".format(data_id))
                # クラス情報
                lines.append("#CLASS\n{}\n".format(self.cls))
                # FaceID
                lines.append("#FACE_ID\n{}\n".format(face_id))
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
                for shape_map in self.shape_map_dict.values():
                    for row in shape_map:
                        for elem in row:
                            f.write(struct.pack(data_format, elem))

    def __str__(self):
        s = super(ShapeMap, self).__str__() + " ( Direction : {} )\n".format(
            self.traverse_direction.name)
        for face_id, shape_map in self.shape_map_dict.items():
            s += "face ID : {}\n".format(face_id)
            for row in shape_map:
                s += "{}\n".format(row)
        return s


class ShapeMapCreator(object):
    """

    三次元モデルから距離マップを取得するクラス

    三次元モデルの重心から、正二十面体グリッド頂点までの線分を定義し、
    線分とモデル表面との交点までの距離を保存したマップを作る

    """

    DIST_UNDEFINED = -1

    def __init__(self, obj3d_path, grd_path, cls, n_div, scale_grid):

        """

        :type obj3d_path: str
        :param obj3d_path: 読み込み３Dオブジェクトのパス

        :type grd_path: str
        :param grd_path: 読み込むグリッドのパス

        :type cls: int
        :param cls: クラスラベル

        :type n_div: int
        :param n_div: グリッドの分割数

        :type scale_grid: float
        :param scale_grid: グリッドのスケール率

        """

        # 3Dモデル
        # モデルを座標系の中心に置き、正規化する
        self.obj3d = Obj3d.load(obj3d_path).center().normal()
        # 正二十面体グリッド（頂点情報はz成分→xyのなす角でソートされる）
        # グリッドが３Dモデルを内部に完全に含むように拡張
        self.grid = IcosahedronGrid.load(grd_path).center().scale(scale_grid)\
            .divide_face(n_div)

        # 3Dモデルの中心から最も離れた点の中心からの距離が、
        # グリッドの中心から最も近い点のより中心からの距離より大きい場合はサポート外
        # （原則、scale_gridは1以上で設定する）
        if np.linalg.norm(self.grid.vertices, axis=1).min() < np.linalg.norm(
                self.obj3d.vertices, axis=1).max():
            raise NotImplementedError()

        self.cls = cls

    def tomas_moller(self, origin, end, v0, v1, v2):
        """

        Tomas-Mollerのアルゴリズム
        線分と三角形の交点を返す
        交差しない場合、Noneを返す

        行列式を、外積/内積に置き換えている

        :type origin: np.ndarray
        :param origin: 線分の始点

        :type end: np.ndarray
        :param end: 線分の終点

        :type v0 : np.ndarray
        :param v0: 三角形の頂点その１

        :type v1: np.ndarray
        :param v1: 三角形の頂点その２

        :type v2: np.ndarray
        :param v2: 三角形の頂点その３

        :rtype: np.ndarray
        :return: 交点ベクトル

        """
        edge1 = v1 - v0
        edge2 = v2 - v0
        ray = end - origin

        P = np.cross(ray, edge2)

        # 分母
        denominator = np.dot(P, edge1)

        if denominator > np.finfo(float).eps:
            T = origin - v0
            u = np.dot(P, T)

            if 0 <= u <= denominator:
                Q = np.cross(T, edge1)
                v = np.dot(Q, ray)

                if 0 <= v <= denominator and (u + v) <= denominator:
                    t = np.dot(Q, edge2) / denominator

                    return origin + ray * t

        return None

    def create(self, directions):
        """

        ShapeMapオブジェクトを生成する

        :type directions: IcosahedronGrid.DIRECTION
        :param directions: IcosahedronGridの頂点走査方向（複数指定可能）

        :rtype: ShapeMap
        :return: ShapeMapオブジェクト

        """

        grid_center = np.zeros(shape=(3,))

        # 距離マップ インデックスはグリッドのverticesに対応する
        # 空洞など、距離が未定義のところにはDIST_UNDEFINED値を入れる
        distances = np.full(shape=(len(self.grid.vertices)),
                            fill_value=ShapeMapCreator.DIST_UNDEFINED,
                            dtype=np.float64)

        # 交点リスト
        cps = [None for _ in xrange(len(distances))]

        for i, g_vertex in enumerate(self.grid.vertices):
            for f0, f1, f2 in self.obj3d.vertices[self.obj3d.face_vertices]:
                p_cross = self.tomas_moller(grid_center, g_vertex, f0, f1, f2)
                if p_cross is not None:
                    dist = np.linalg.norm(p_cross - grid_center)
                    distances[i] = dist
                    cps[i] = p_cross
                    break

        # FaceIDと頂点インデックスのマップの辞書を取得
        shape_maps = []
        for direction in directions:
            traversed_indices_dict = self.grid.traverse(direction)

            distance_maps = [[[distances[idx]
                               if idx != IcosahedronGrid.VERTEX_IDX_UNDEFINED
                               else ShapeMapCreator.DIST_UNDEFINED
                               for idx in row]
                              for row in indices_map]
                             for indices_map in traversed_indices_dict.values()]

            shape_maps.append(ShapeMap(traversed_indices_dict.keys(),
                                       distance_maps, self.cls, self.grid.n_div,
                                       direction))
        return shape_maps

    def create_all_direction(self):
        return self.create(directions=(IcosahedronFace.DIRECTION.HORIZON,
                                       IcosahedronFace.DIRECTION.UPPER_RIGHT,
                                       IcosahedronFace.DIRECTION.UPPER_LEFT))
