#!/usr/bin/env python
# coding: utf-8

import os
import struct
import pprint
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

    DIST_UNDEFINED = -1

    def __init__(self, obj3d_path, grd_path, n_div, scale_grid):

        # 3Dモデル
        self.obj3d = Obj3d.load(obj3d_path)
        # 正二十面体グリッド（頂点情報はz成分→xyのなす角でソートされる）
        self.grid = Grid.load(grd_path)

        # モデルを座標系の中心に置き、正規化する
        self.obj3d.center()
        self.obj3d.normal()

        # グリッドが３Dモデルを内部に完全に含むように拡張
        self.grid.center()
        self.grid.scale(scale_grid)

        # グリッドを分割
        self.grid.divide_face(n_div)

        # 3Dモデルの中心から最も離れた点の中心からの距離が、
        # グリッドの中心から最も近い点のより中心からの距離より大きい場合はサポート外
        # （原則、scale_gridは1以上で設定する）
        if np.linalg.norm(self.grid.vertices, axis=1).min() < np.linalg.norm(
                self.obj3d.vertices, axis=1).max():
            raise NotImplementedError()

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

        grid_center = np.zeros(shape=(3,))

        # 距離マップ インデックスはグリッドのverticesに対応する
        distance = []

        for v_grid in self.grid.vertices:
            for fv_obj3d in self.obj3d.faces:
                f0, f1, f2 = self.obj3d.vertices[fv_obj3d]
                p_cross = self.tomas_moller(grid_center, v_grid, f0, f1, f2)
                if p_cross is not None:
                    dist = np.linalg.norm(p_cross - grid_center)
                    distance.append(dist)
                    break
            else:
                # 空洞など、距離が未定義のところにはDIST_UNDEFINED値を入れる
                distance.append(ShapeMap.DIST_UNDEFINED)

        distance = np.array(distance)

        # 距離が最大となるグリッド頂点の所属するFaceInfo
        face_id_max_dist = [f_info
                            for f_info in self.grid.face_info
                            for v_info in f_info.vertex_info
                            if v_info.vertex_idx == distance.argmax()][0]

        upper_v_info = self.grid.traverse(face_id_max_dist, 'upper',
                                          n_face_traverse=8)
        lower_v_info = self.grid.traverse(face_id_max_dist, 'lower',
                                          n_face_traverse=8)
        horizontal_v_info = self.grid.traverse(face_id_max_dist, 'horizontal',
                                               n_face_traverse=10)

        def dist_map_from_info(vertex_info):
            return [[distance[v_info.vertex_idx]
                     if v_info is not None
                     else ShapeMap.DIST_UNDEFINED
                     for v_info in row]
                    for row in vertex_info]

        upper_distance = dist_map_from_info(upper_v_info)
        lower_distance = dist_map_from_info(lower_v_info)
        horizontal_distance = dist_map_from_info(horizontal_v_info)


        return upper_distance, lower_distance, horizontal_distance


if __name__ == '__main__':
    map = ShapeMap(obj3d_path="../res/stanford_bunny.obj",
                   grd_path="../res/new_regular_ico.grd",
                   n_div=3,
                   scale_grid=2)

    upper_distance, lower_distance, horizontal_distance = map.dist()

    # pprint.pprint(map.dist())
