#!/usr/bin/env python
# coding: utf-8

import os
import struct
import numpy as np
from numpy import linalg
from obj3d import Obj3d
from grid import Grid


class ShapeMap(object):
    """

    三次元モデルから距離マップを取得するクラス

    三次元モデルの重心から、正二十面体グリッド頂点までの線分を定義し、
    線分とモデル表面との交点までの距離を保存したマップを作る

    """

    def __init__(self, obj3d_path, grd_path, n_div, scale_grid):

        # 3Dモデル
        self.obj3d = Obj3d.load(obj3d_path)
        # 正二十面体グリッド（頂点情報はz成分→xyのなす角でソートされる）
        self.grid = Grid.load(grd_path).divide_face(n_div)

        # モデルを座標系の中心に置き、正規化する
        self.obj3d.center()
        self.obj3d.normal()

        # グリッドが３Dモデルを内部に完全に含むように拡張
        self.grid.scale(scale_grid)

        # 3Dモデルの中心から最も離れた点の中心からの距離が、
        # グリッドの中心から最も近い点のより中心からの距離より大きい場合はサポート外
        # （原則、scale_gridは1以上で設定する）
        if np.linalg.norm(self.grid.vertices, axis=1).min() < np.linalg.norm(
                self.obj3d.vertices, axis=1).max():
            raise NotImplementedError()

    def tomas_moller(self, origin, end, v0, v1, v2):
        """

        Tomas-Mollerのアルゴリズム
        線分が三角形の交点を返す
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
        denominator = linalg.det(np.vstack((edge1, edge2, -ray)))

        if denominator > 0:
            T = origin - v0
            u = np.dot(P, T)

            if 0 <= u <= denominator:
                Q = np.cross(T, edge1)
                v = np.dot(Q, ray)

                if 0 <= v <= denominator and (u + v) <= denominator:
                    t = np.dot(Q, edge2) / denominator

                    return origin + ray * t

        return None

    # def dist(self, is_sorted_by_z):
    #     """
    #
    #     距離マップを得る
    #
    #     is_sorted_by_z=Trueで距離マップはリストの入れ子構造になる
    #     z成分が同じである頂点座標の距離情報は同一のリストに入り、
    #     各リストはz成分の大きさでソートされる
    #
    #     ex.
    #     [
    #     z=1 → [a1]
    #     z=0.33 → [b1, b2, ... ,b5]
    #     z=-0.33 → [c1, c2, ... ,c5]
    #     z=-1 → [d1]
    #     ]
    #     (上記リスト内の各要素は距離を表す)
    #
    #     :type is_sorted_by_z: bool
    #     :param is_sorted_by_z: 距離情報をリストの入れ子構造にするかどうか
    #     :rtype: np.ndarray
    #     :return: 距離マップ
    #
    #     """
    #
    #     distances = np.empty(shape=(len(self.grid.vertices),))
    #
    #     # 中心座標へのベクトル
    #     v_center = np.mean(self.model.vertices, axis=0)
    #
    #     for idx_dist, v_grid in enumerate(self.grid.vertices):
    #
    #         v_grid_from_center = v_grid - v_center
    #
    #         for f_model in self.model.faces:
    #
    #             f0, f1, f2 = self.model.vertices[f_model]
    #
    #             # ベクトルの正負を正すため、逆順に頂点情報を入れる
    #             p = self.tomas_moller(v_center, v_grid_from_center, f2, f1, f0)
    #
    #             if p is not None:
    #                 distances[idx_dist] = linalg.norm(p)
    #                 break
    #
    #     if is_sorted_by_z:
    #         parents = []
    #         children = []
    #         z = self.grid.vertices[0][2]
    #         for i, v_grid in enumerate(self.grid.vertices):
    #             vz = v_grid[2]
    #             if z != vz:
    #                 parents.append(children)
    #                 children = []
    #             children.append(distances[i])
    #             z = vz
    #         else:
    #             parents.append(children)
    #         distances = parents
    #
    #     return distances
    #
    # @staticmethod
    # def save_dstm(file_path, distances):
    #
    #     """
    #
    #     dstmファイル形式で距離マップを保存する
    #
    #     :type file_path: str
    #     :param file_path: 保存するファイルのパス
    #     :type distances: list(list)
    #     :param distances: 入れ子構造の距離マップ
    #
    #     """
    #
    #     # distances型チェック
    #     assert isinstance(distances, list)
    #
    #     # 拡張子チェック
    #     f_name, ext = os.path.splitext(file_path)
    #     if ext != '.dstm':
    #         file_path = f_name + '.dstm'
    #
    #     with open(file_path, mode='wb') as f:
    #
    #         f.writelines("# DSTM\n")
    #         f.writelines("# N_COLUMN\n")
    #
    #         for dists in distances:
    #             f.writelines(str(len(dists)) + "\n")
    #
    #         f.writelines("# DATA(DOUBLE)\n")
    #
    #         for dists in distances:
    #             for d in dists:
    #                 f.write(struct.pack('f', d))
    #
    # @staticmethod
    # def load_dstm(file_path):
    #     """
    #
    #     dstmファイル形式の距離マップを読み込み、入れ子リスト構造で返す
    #
    #     :type file_path: str
    #     :param file_path: 読み込むファイルのパス
    #     :rtype : list(list)
    #     :return: 入れ子リスト構造の距離マップ
    #     """
    #
    #     # 拡張子チェック
    #     f_name, ext = os.path.splitext(file_path)
    #     if ext != '.dstm':
    #         file_path = f_name + '.dstm'
    #
    #     distances = []
    #     n_column = []
    #
    #     with open(file_path, mode='rb') as f:
    #
    #         assert f.readline() == '# DSTM\n'
    #         assert f.readline() == '# N_COLUMN\n'
    #
    #         while True:
    #             line = f.readline()
    #             if line == '# DATA(DOUBLE)\n':
    #                 break
    #             n_column.append(int(line))
    #
    #         for nc in n_column:
    #             column = []
    #             for i in xrange(nc):
    #                 column.append(struct.unpack('f', f.read(4))[0])
    #             distances.append(column)
    #
    #     return distances
