#!/usr/bin/env python
# coding: utf-8

import numpy as np
from src.obj.obj3d import Obj3d
from src.obj.grid.base_grid import BaseGrid


class BaseShapeMapFactory(object):

    DIST_UNDEFINED = -1

    def __init__(self, obj3d, grid, n_div, cls, grid_scale):
        """

        :type obj3d: Obj3d
        :param obj3d: 形状マップ生成対象の３Dオブジェクト

        :type grid: TriangleGrid
        :param grid: 形状マップを生成するための正三角形からなるグリッド

        :type n_div: int or long
        :param n_div: グリッド分割数

        :type cls: int or long
        :param cls: クラスラベル

        :type grid_scale: float
        :param grid_scale: グリッドのスケール率

        """

        assert isinstance(obj3d, Obj3d)
        assert isinstance(grid, BaseGrid)
        assert isinstance(cls, (int, long))
        assert isinstance(grid_scale, float)

        # 3Dモデル:座標系の中心に置き、正規化する
        self.obj3d = obj3d.center().normal()
        # 正二十面体グリッド:３Dモデルを内部に完全に含むように拡張
        self.grid = grid.center().scale(grid_scale).divide_face(n_div)

        # 3Dモデルの中心から最も離れた点の中心からの距離が、
        # グリッドの中心から最も近い点のより中心からの距離より大きい場合はサポート外
        # （原則、scale_gridは1以上で設定する）
        if np.linalg.norm(self.grid.vertices, axis=1).min() < np.linalg.norm(
                self.obj3d.vertices, axis=1).max():
            raise NotImplementedError()

        # クラスラベル
        self.cls = cls

    @staticmethod
    def tomas_moller(origin, end, v0, v1, v2):
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

    def create(self):
        raise NotImplementedError

    def _distances(self):
        """

        グリッド頂点に対応した距離情報のマップを取得する

        """

        grid_center = np.zeros(shape=(3,))

        # 距離マップ インデックスはグリッドのverticesに対応する
        # 空洞など、距離が未定義のところにはDIST_UNDEFINED値を入れる
        distance_map = np.full(shape=(len(self.grid.vertices)),
                               fill_value=BaseShapeMapFactory.DIST_UNDEFINED,
                               dtype=np.float64)

        for i, g_vertex in enumerate(self.grid.vertices):
            for f0, f1, f2 in self.obj3d.vertices[self.obj3d.face_vertices]:
                p_cross = self.tomas_moller(grid_center, g_vertex, f0, f1, f2)
                if p_cross is not None:
                    distance_map[i] = np.linalg.norm(p_cross - grid_center)
                    break

        return distance_map
