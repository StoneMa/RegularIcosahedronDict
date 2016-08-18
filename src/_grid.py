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

    def __init__(self, vertices, grid_face, n_div):
        """

        :type vertices: list or tuple or np.ndarray
        :param vertices: 全頂点情報

        :type grid_faces: list or tuple
        :param grid_faces: 多角形グリッドの各面の情報

        :type n_div: int
        :param n_div: Grid3dオブジェクトの各面の分割数

        """
        super(Grid3d, self).__init__(vertices)
        self.grid_faces = tuple(grid_face)
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
