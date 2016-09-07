#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
from triangle_grid import TriangleGrid, TriangleFace


class IcosahedronGrid(TriangleGrid):
    """
    距離マップ生成用グリッドクラス
    face情報・normal情報は失われる
    代わりに各グリッド面の情報GridFaceが保持される
    """

    VERTEX_IDX_UNDEFINED = None

    def __init__(self, vertices, grid_faces, n_div):
        """

        :type vertices: list or tuple or np.ndarray
        :param vertices: 全頂点情報

        :type grid_faces: list or tuple
        :param grid_faces: 多角形グリッドの各面の情報

        :type n_div: int
        :param n_div: Grid3dオブジェクトの各面の分割数

        """
        super(IcosahedronGrid, self).__init__(vertices,grid_faces, 20)
        self.grid_faces = tuple(grid_faces)
        self.n_div = n_div

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

        with open(grd_file) as f:

            for line in f.readlines():

                line = line.strip().split()

                if len(line) == 0 or line[0] == '#':
                    continue

                if line[0] == 'v':
                    vertices.append(map(float, line[1:]))

                elif line[0] == 'f':
                    face_vertices.append(map(int, line[1:]))

        vertices = np.asarray(vertices)

        grid_faces = [TriangleFace(face_id,
                                   vidx_table={(0, 0): fv[0], (1, 0): fv[1],
                                               (0, 1): fv[2]})
                      for face_id, fv in enumerate(face_vertices)]

        return IcosahedronGrid(vertices, grid_faces, 1)

    def divide_face(self, n_div, epsilon=np.finfo(float).eps):
        """

        指定数で面を分割したGrid3dオブジェクトを返す

        :type n_div: int
        :param n_div: 分割数

        :type epsilon: float
        :param epsilon: 浮動小数点座標を等号比較する時の許容誤差

        :rtype : IcosahedronGrid
        :return : 分割後のGrid3dオブジェクト

        """

        new_vertices = np.empty(shape=(0, 3))

        new_grid_faces = []

        for grid_face in self.grid_faces:

            # グリッド面の三頂点
            top_vertex = self.vertices[grid_face.top_vertex_idx()]
            left_vertex = self.vertices[grid_face.left_vertex_idx()]
            right_vertex = self.vertices[grid_face.right_vertex_idx()]

            left_vector = left_vertex - top_vertex
            right_vector = right_vertex - top_vertex

            # 一旦GridFaceの頂点情報をクリア
            new_face = TriangleFace(grid_face.face_id, n_div=n_div)

            for sum_length in xrange(n_div + 1):
                for i in xrange(sum_length + 1):
                    alpha = sum_length - i
                    beta = i
                    new_vertex = left_vector * float(
                        alpha) / n_div + right_vector * float(
                        beta) / n_div + top_vertex

                    # 重複チェック
                    check_duplicate = (
                        np.abs(new_vertex - new_vertices) < epsilon).all(axis=1)

                    if len(new_vertices) > 0 and check_duplicate.any():
                        v_idx = int(np.argwhere(check_duplicate))
                    else:
                        v_idx = len(new_vertices)
                        new_vertices = np.vstack((new_vertices, new_vertex))

                    # 新しく頂点情報を追加
                    new_face.set_vertex_idx(v_idx, alpha, beta)

            new_grid_faces.append(new_face)

        return IcosahedronGrid(new_vertices, new_grid_faces, n_div)

    def find_face_from_id(self, face_id):
        """

        指定したface_idを持つGridFaceを返す
        指定したface_idを持つGridFaceが見つからない場合、IndexErrorを投げる

        :type face_id: int
        :param face_id: 要求するGridFaceのID

        :rtype: IcosahedronFace
        :return: 指定したface_idを持つGridFace

        """
        for grid_face in self.grid_faces:
            if grid_face.face_id == face_id:
                return grid_face
        else:
            raise IndexError

    def traverse(self, direction):
        """

        正二十面体グリッドの各面の頂点インデックスを走査し、
        結果をFaceIDとのペアで返す

        :type direction: IcosahedronFace.DIRECTION
        :param direction: 走査方向

        :rtype dict
        :return FaceIDをキー、面の頂点インデックスリストをバリューとした辞書

        """
        return {grid_face.face_id: grid_face.traverse(direction)
                for grid_face in self.grid_faces}

    def center(self):
        """

        頂点群の重心が座標軸の原点となるように、全ての頂点座標を平行移動する

        :rtype: IcosahedronGrid
        :return: 平行移動後のIcosahedronGridオブジェクト

        """
        obj3d = super(IcosahedronGrid, self).center()
        return IcosahedronGrid(obj3d.vertices, self.grid_faces_as_copy(),
                               self.n_div)

    def normal(self):
        """

        重心から頂点までの距離が最大1となるように、全ての頂点座標を正規化する

        :rtype: IcosahedronGrid
        :return: 正規化後のIcosahedronGridオブジェクト

        """
        obj3d = super(IcosahedronGrid, self).normal()
        return IcosahedronGrid(obj3d.vertices, self.grid_faces_as_copy(),
                               self.n_div)

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
                               self.n_div)

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
                               self.n_div)

    def grid_faces_as_copy(self):
        """
        IcosahedronGridオブジェクトの保持するIcosahedronFaceリストをコピーして返す

        :rtype: list(IcosahedronFace)
        :return: IcosahedronFaceのリストのコピー

        """
        return [TriangleFace(gf.face_id, n_div=gf.n_div,
                             vidx_table=gf.vidx_table_as_copy()) for gf in
                self.grid_faces]

    def __str__(self):
        """

        :rtype: str
        :return: str化した時のIcosahedronGridの文字列

        """
        s = super(IcosahedronGrid, self).__str__() + "(n_div={}) : \n".format(
            self.n_div)
        for grid_face in self.grid_faces:
            s += grid_face.__str__() + "\n"
        return s
