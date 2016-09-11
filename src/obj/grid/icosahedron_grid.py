#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
from triangle_grid import TriangleGrid, TriangleFace


class IcosahedronGrid(TriangleGrid):
    """
    距離マップ生成用グリッドクラス
    face_vertex情報・normal_vertex情報は失われる
    代わりに各グリッド面の情報GridFaceが保持される
    """

    N_FACE = 20

    def __init__(self, vertices, grid_faces, n_div, upper_direction):
        """

        :type vertices: list or tuple or np.ndarray
        :param vertices: 全頂点情報

        :type grid_faces: list or tuple
        :param grid_faces: 多角形グリッドの各面の情報

        :type n_div: int
        :param n_div: Grid3dオブジェクトの各面の分割数

        :type upper_direction: (float, float, float)
        :param upper_direction: グリッドの上方向を表す単位ベクトル

        """
        super(IcosahedronGrid, self).__init__(vertices, grid_faces,
                                              IcosahedronGrid.N_FACE, n_div,
                                              upper_direction)

    @staticmethod
    def load(grd_file):
        """

        .grd形式のファイルを読み込み、Grid3dオブジェクトを返す

        :type grd_file: str
        :param grd_file: .grd形式のファイルパス

        :rtype : IcosahedronGrid
        :return : Grid3dオブジェクト

        """

        if os.path.splitext(grd_file)[-1] != ".grd":
            raise IOError(
                "IcoGrid::__init__ : file path is incorrect : {}".format(
                    grd_file))

        vertices = []
        face_vertices = []
        adjacent_face_ids = []
        upper_direction = None

        with open(grd_file) as f:

            for line in f.readlines():

                line = line.strip().split()

                if len(line) == 0 or line[0] == '#':
                    continue

                if line[0] == 'v':
                    vertices.append(map(float, line[1:]))

                elif line[0] == 'f':
                    face_vertices.append(map(int, line[1:]))

                elif line[0] == 'af':
                    adjacent_face_ids.append(map(int, line[1:]))

                elif line[0] == 'ud':
                    upper_direction = tuple(map(float, line[1:]))

        assert len(face_vertices) == len(adjacent_face_ids)

        grid_faces = [TriangleFace(face_id,
                                   left_face_id=af[0],
                                   right_face_id=af[1],
                                   bottom_face_id=af[2],
                                   vidx_table={(0, 0): fv[0], (1, 0): fv[1],
                                               (0, 1): fv[2]})
                      for face_id, fv, af in zip(xrange(len(face_vertices)),
                                                 face_vertices,
                                                 adjacent_face_ids)]

        return IcosahedronGrid(np.asarray(vertices), grid_faces, 1,
                               upper_direction)

    def center(self):
        """

        頂点群の重心が座標軸の原点となるように、全ての頂点座標を平行移動する

        :rtype: IcosahedronGrid
        :return: 平行移動後のIcosahedronGridオブジェクト

        """
        obj3d = super(IcosahedronGrid, self).center()
        return IcosahedronGrid(obj3d.vertices, self.grid_faces_as_copy(),
                               self.n_div, self.upper_direction)

    def normal(self):
        """

        重心から頂点までの距離が最大1となるように、全ての頂点座標を正規化する

        :rtype: IcosahedronGrid
        :return: 正規化後のIcosahedronGridオブジェクト

        """
        obj3d = super(IcosahedronGrid, self).normal()
        return IcosahedronGrid(obj3d.vertices, self.grid_faces_as_copy(),
                               self.n_div, self.upper_direction)

    def scale(self, r):
        """

        頂点群の重心から各頂点までの距離をr倍する

        :type r: float
        :param r: 距離倍率

        :rtype: IcosahedronGrid
        :return: スケーリングしたIcosahedronGridオブジェクト

        """
        obj3d = super(IcosahedronGrid, self).scale(r)
        return IcosahedronGrid(obj3d.vertices, self.grid_faces_as_copy(),
                               self.n_div, self.upper_direction)

    def rotate(self, theta, axis_vector):
        """

        頂点群をaxis_vectorを軸として角度thetaだけ回転する

        :type theta: float
        :param theta: 回転角

        :type axis_vector: np.ndarray
        :param axis_vector: 軸ベクトル

        :rtype: IcosahedronGrid
        :return: 回転後IcosahedronGridオブジェクト
        """
        obj3d = super(IcosahedronGrid, self).rotate(theta, axis_vector)
        return IcosahedronGrid(obj3d.vertices, self.grid_faces_as_copy(),
                               self.n_div, self.upper_direction)

    def grid_faces_as_copy(self):
        """
        IcosahedronGridオブジェクトの保持するTriangleFaceリストをコピーして返す

        :rtype: list(IcosahedronFace)
        :return: TriangleFaceのリストのコピー

        """
        return [TriangleFace(gf.face_id,
                             left_face_id=gf.left_face_id,
                             right_face_id=gf.right_face_id,
                             bottom_face_id=gf.bottom_face_id,
                             n_div=gf.n_div,
                             vidx_table=gf.vidx_table_as_copy()) for gf in
                self.grid_faces]
