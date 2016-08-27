#!/usr/bin/env python
# coding: utf-8

import struct
import numpy as np
from numpy import linalg
from _obj3d import _Obj3d
from _grid import Grid3d, GridFace


class DistanceMap(object):
    """

    三次元モデルから距離マップを取得するクラス

    三次元モデルの重心から、正二十面体グリッド頂点までの線分を定義し、
    線分とモデル表面との交点までの距離を保存したマップを作る

    """

    DIST_UNDEFINED = -1

    def __init__(self, obj3d_path, grd_path, n_div, scale_grid):

        # 3Dモデル
        # モデルを座標系の中心に置き、正規化する
        self.obj3d = _Obj3d.load(obj3d_path).center().normal()
        # 正二十面体グリッド（頂点情報はz成分→xyのなす角でソートされる）
        # グリッドが３Dモデルを内部に完全に含むように拡張
        self.grid = Grid3d.load(grd_path).center().scale(scale_grid) \
            .divide_face(n_div)

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

    def distance_map(self):

        def dist():

            grid_center = np.zeros(shape=(3,))

            # 距離マップ インデックスはグリッドのverticesに対応する
            dists = np.empty(shape=(len(self.grid.vertices)))
            # 交点リスト
            cps = [None for i in xrange(len(dists))]

            for i, v_grid in enumerate(self.grid.vertices):
                for fv_obj3d in self.obj3d.face_vertices:
                    f0, f1, f2 = self.obj3d.vertices[fv_obj3d]
                    p_cross = self.tomas_moller(grid_center, v_grid, f0, f1, f2)
                    if p_cross is not None:
                        dist = np.linalg.norm(p_cross - grid_center)
                        dists[i] = dist
                        cps[i] = p_cross
                        break
                else:
                    # 空洞など、距離が未定義のところにはDIST_UNDEFINED値を入れる
                    dists[i] = DistanceMap.DIST_UNDEFINED

            return dists, cps

        # 一旦距離を取得
        distance, cross_points = dist()

        '''
         グリッドの頂点Pとモデルの重心Gを結び、PGとモデル表面の交点をQとし、
         GQが最大となるような交点をQ'としたとき、FaceID=0の面のtop_vertexがGPの延長上に
         なるようにモデルを回転する処理
        '''

        # 重心との距離が最大となるモデル上の交点
        max_dist_cp = cross_points[distance.argmax()]

        if max_dist_cp is None:
            raise IndexError

        # face_id=0の面のtop_vertex
        top_vertex_face_0 = \
            self.grid.vertices[self.grid.find_face_from_id(0).top_vertex_idx()]

        # 回転軸ベクトル（外積）
        axis = np.cross(max_dist_cp, top_vertex_face_0)

        # モデル上の交点とtop_vertexのなす角度
        theta = np.arcsin(np.linalg.norm(axis) / (
            np.linalg.norm(max_dist_cp) * np.linalg.norm(top_vertex_face_0)))

        # モデルを回転
        self.obj3d = self.obj3d.rotate(theta, axis)

        # 再度距離を取得
        distance, cross_points = dist()

        # 頂点インデックスのマップを取得
        horizon_idx_map, to_lower_right_idx_map, to_upper_right_idx_map = self.grid.traverse()

        def dist_map_from_vertex_index_map(vertex_index_map):
            return [[distance[v_idx]
                     if v_idx is not Grid3d.VERTEX_IDX_UNDEFINED
                     else DistanceMap.DIST_UNDEFINED
                     for v_idx in row]
                    for row in vertex_index_map]

        horizon_dist_map = dist_map_from_vertex_index_map(horizon_idx_map)
        to_lower_right_dist_map = dist_map_from_vertex_index_map(
            to_lower_right_idx_map)
        to_upper_right_dist_map = dist_map_from_vertex_index_map(
            to_upper_right_idx_map)

        return horizon_dist_map, to_lower_right_dist_map, to_upper_right_dist_map

    @staticmethod
    def save_map_as_dstm(horizon_distance_map, lower_distance_map,
                         upper_distance_map, dstm_file_path, data_format='f'):
        """

        距離マップを.dstmファイル形式で保存する

        """

        maps = (("HORIZON", horizon_distance_map),
                ("LOWER", lower_distance_map),
                ("UPPER", upper_distance_map))

        lines = []

        with open(dstm_file_path, mode='wb') as f:

            lines.append("#DSTM\n")

            for name, distance_map in maps:
                lines.append("#N_COLUMN {}\n".format(name))
                for row in distance_map:
                    lines.append(str(len(row)) + "\n")

            lines.append("#DATA(DATA_FORMAT:{})\n".format(data_format))
            f.writelines(lines)

            for _, distance_map in maps:
                for row in distance_map:
                    for elem in row:
                        f.write(struct.pack(data_format, elem))


if __name__ == '__main__':
    map = DistanceMap(obj3d_path="../res/stanford_bunny.obj",
                      grd_path="../res/new_regular_ico.grd",
                      n_div=2,
                      scale_grid=2)

    horizon_dist_map, to_lower_right_dist_map, to_upper_right_dist_map = map.distance_map()

    for h_row in horizon_dist_map:
        row = "["
        for h in h_row:
            row += "%4f " % h
        print row + "]"
