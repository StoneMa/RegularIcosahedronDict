#!/usr/bin/env python
# coding: utf-8

import numpy as np
from numpy import linalg
from model import Model
from regular_icosahedron import RegularIcosahedron


class Map2D(object):
    """

    三次元モデルから距離マップを取得するクラス

    三次元モデルの重心から、正二十面体グリッド頂点までの線分を定義し、
    線分とモデル表面との交点までの距離を保存したマップを作る

    """

    def __init__(self, model_path, grid_path, n_div_recursion, scale_grid):

        # 3Dモデル
        self.model = Model.load(model_path)
        # 正二十面体グリッド
        self.grid = RegularIcosahedron.division(n_div_recursion,
                                                RegularIcosahedron.load(
                                                    grid_path))

        # モデルを座標系の中心に置き、正規化する
        Model.center(self.model)
        Model.normal(self.model)

        # グリッドが３Dモデルを内部に完全に含むように拡張
        RegularIcosahedron.scale(self.grid, scale_grid)

        # 3Dモデルの中心から最も離れた点の中心からの距離が、
        # グリッドの中心から最も近い点のより中心からの距離より大きい場合はサポート外
        # （原則、scale_gridは1以上で設定する）
        if np.linalg.norm(self.grid.vertices, axis=1).min() < np.linalg.norm(
                self.model.vertices, axis=1).max():
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

    def dist(self):
        """

        距離マップを得る

        :rtype: np.ndarray
        :return: 距離マップ

        """

        distances = np.empty(shape=(len(self.grid.vertices),))

        # 中心座標へのベクトル
        v_center = np.mean(self.model.vertices, axis=0)

        for idx_dist, v_grid in enumerate(self.grid.vertices):

            v_grid_from_center = v_grid - v_center

            for f_model in self.model.faces:

                f0, f1, f2 = self.model.vertices[f_model]

                # ベクトルの正負を正すため、逆順に頂点情報を入れる
                p = self.tomas_moller(v_center, v_grid_from_center, f2, f1, f0)

                if p is not None:
                    distances[idx_dist] = linalg.norm(p)
                    break

        return distances


