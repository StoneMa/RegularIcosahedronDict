#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
from collections import OrderedDict
from src._obj3d import _Obj3d


class Grid3d(_Obj3d):
    """
    距離マップ生成用グリッドクラス
    face情報・normal情報は失われる
    代わりに各グリッド面の情報GridFaceが保持される
    """

    def __init__(self, vertices, grid_faces, n_div):
        """

        :type vertices: list or tuple or np.ndarray
        :param vertices: 全頂点情報

        :type grid_faces: list or tuple
        :param grid_faces: 多角形グリッドの各面の情報

        :type n_div: int
        :param n_div: Grid3dオブジェクトの各面の分割数

        """
        super(Grid3d, self).__init__(vertices)
        self.grid_faces = tuple(grid_faces)
        self.n_div = n_div

    @staticmethod
    def load(grd_file):
        """

        .grd形式のファイルを読み込み、Grid3dオブジェクトを返す

        :type grd_file: str
        :param grd_file: .grd形式のファイルパス

        :rtype : Grid3d
        :return : Grid3dオブジェクト
        """

        if os.path.splitext(grd_file)[-1] != ".grd":
            raise IOError(
                "IcoGrid::__init__ : file path is incorrect : {}".format(
                    grd_file))

        vertices = []
        face_vertices = []
        adjacent_faces = []

        with open(grd_file) as f:

            for line in f.readlines():

                line = line.strip().split()

                if len(line) == 0 or line[0] == '#':
                    continue

                if line[0] == 'v':
                    vertices.append(map(float, line[1:]))

                if line[0] == 'f':
                    face_vertices.append(map(int, line[1:]))

                if line[0] == 'af':
                    adjacent_faces.append(map(int, line[1:]))

            vertices = np.asarray(vertices)

            grid_faces = np.array([GridFace(face_id, None, None, None)
                                   for face_id, fv in enumerate(face_vertices)])

            for grid_face, fv, af in zip(grid_faces, face_vertices,
                                         adjacent_faces):
                top_vertex_idx, left_vertex_idx, right_vertex_idx = fv

                grid_face.set_vertex_idx(idx=top_vertex_idx, alpha=0, beta=0)
                grid_face.set_vertex_idx(idx=left_vertex_idx, alpha=1, beta=0)
                grid_face.set_vertex_idx(idx=right_vertex_idx, alpha=0, beta=1)

                left_face, right_face, bottom_face = grid_faces[af]

                grid_face.left_face = left_face
                grid_face.right_face = right_face
                grid_face.bottom_face = bottom_face

        return Grid3d(vertices, grid_faces, n_div=1)

    def divide_face(self, n_div, epsilon=np.finfo(float).eps):
        """

        指定数で面を分割したGrid3dオブジェクトを返す

        :type n_div: int
        :param n_div: 分割数

        :type epsilon: float
        :param epsilon: 浮動小数点座標を等号比較する時の許容誤差

        :rtype : Grid3d
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
            new_face = GridFace(grid_face.face_id, None, None, None)

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

        # 新しいGridFaceのleft_face,right_face,bottom_faceをセットする
        for new_face, old_face in zip(new_grid_faces, self.grid_faces):
            new_face.left_face = new_grid_faces[old_face.left_face.face_id]
            new_face.right_face = new_grid_faces[old_face.right_face.face_id]
            new_face.bottom_face = new_grid_faces[old_face.bottom_face.face_id]

        return Grid3d(new_vertices, new_grid_faces, n_div)

    def __str__(self):
        s = super(Grid3d, self).__str__() + "(n_div={}) : \n".format(self.n_div)
        for grid_face in self.grid_faces:
            s += grid_face.__str__() + "\n"
        return s


class GridFace(object):
    def __init__(self, face_id, left_face, right_face, bottom_face):
        self.face_id = face_id

        self.__vertices_idx = OrderedDict()

        self.left_face = left_face
        self.right_face = right_face
        self.bottom_face = bottom_face

    def set_vertex_idx(self, idx, alpha, beta):
        self.__vertices_idx[(alpha, beta)] = idx

    def get_vertex_idx(self, alpha, beta):
        return self.__vertices_idx[(alpha, beta)]

    def top_vertex_idx(self):
        return self.get_vertex_idx(0, 0)

    def left_vertex_idx(self):
        return self.get_vertex_idx(1, 0)

    def right_vertex_idx(self):
        return self.get_vertex_idx(0, 1)

    def get_coordinates(self, vertex_idx):
        return [k for k, v in self.__vertices_idx.items() if v == vertex_idx]

    def __str__(self):
        s = "[face ID : {}]\n".format(self.face_id) + \
            "left face : {}\nright face : {}\nbottom face : {}\n".format(
                self.left_face.face_id, self.right_face.face_id,
                self.bottom_face.face_id) + \
            "vertex indices : (alpha, beta) -> [idx]\n"
        for key, idx in self.__vertices_idx.items():
            alpha, beta = key
            s += "({0:^3},{1:^3}) -> {2:^2}\n".format(alpha, beta, idx)
        return s
