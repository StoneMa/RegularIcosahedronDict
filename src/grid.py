#!/usr/bin/env python
# coding: utf-8


import os
import numpy as np
from obj3d import Obj3d


class Grid(Obj3d):
    """
    距離マップ生成用グリッドクラス
    face情報・normal情報は失われる
    代わりに各グリッド面の情報FaceInfoが保持される
    """

    EPSILON = np.finfo(np.float).eps

    def __init__(self, vertices, face_info):

        super(Grid, self).__init__(vertices, None, None, Obj3d.FILE_TYPE.GRD)

        self.face_info = face_info

    @staticmethod
    def load(grd_file):

        if os.path.splitext(grd_file)[-1] != ".grd":
            raise IOError(
                "IcoGrid::__init__ : file path is incorrect : {}".format(
                    grd_file))

        vertices = []
        faces = []
        adjacent_faces = []

        face_info = []

        with open(grd_file) as f:

            for line in f.readlines():

                line = line.strip().split()

                if len(line) == 0 or line[0] == '#':
                    continue

                if line[0] == 'v':
                    vertices.append(np.array(map(float, line[1:])))

                if line[0] == 'f':
                    faces.append(np.array(map(int, line[1:])))

                if line[0] == 'af':
                    adjacent_faces.append(np.array(map(int, line[2:])))

            for fid, fv in enumerate(faces):
                face_info.append(
                    Grid.FaceInfo(fid,
                                  Grid.VertexInfo(fv[0], fid, 0, 0),
                                  Grid.VertexInfo(fv[1], fid, 1, 0),
                                  Grid.VertexInfo(fv[2], fid, 0, 1),
                                  None, None, None))

            for f_info in face_info:
                f_info.left_face_info, \
                f_info.right_face_info, \
                f_info.bottom_face_info = adjacent_faces[f_info.face_id]

        return Grid(vertices, face_info)

    def divide_face(self, n_div):

        new_vertices = np.empty(shape=(0, 3))

        for f_info in self.face_info:
            top_vertex = self.vertices[f_info.top_vertex_info.vertex_idx]
            left_vertex = self.vertices[f_info.left_vertex_info.vertex_idx]
            right_vertex = self.vertices[f_info.right_vertex_info.vertex_idx]

            left_vector = left_vertex - top_vertex
            right_vector = right_vertex - top_vertex

            new_vertex_info = []

            for sum_length in xrange(n_div + 1):
                for i in xrange(sum_length + 1):
                    alpha = float(sum_length - i) / n_div
                    beta = float(i) / n_div
                    new_vertex = left_vector * alpha + right_vector * beta + top_vertex

                    # 重複チェック
                    check_duplicate = (
                        np.abs(new_vertex - new_vertices) < Grid.EPSILON).all(
                        axis=1)

                    length_new_vertices = len(new_vertices)

                    if length_new_vertices > 0 and check_duplicate.any():
                        v_idx = int(np.argwhere(check_duplicate))
                    else:
                        v_idx = length_new_vertices
                        new_vertices = np.vstack((new_vertices, new_vertex))

                    new_vertex_info.append(
                        Grid.VertexInfo(v_idx, f_info.face_id, alpha, beta))

            f_info.vertex_info = new_vertex_info

        self.vertices = new_vertices

    def save(self, file_name):
        name, ext = os.path.splitext(file_name)
        if ext != ".off":
            file_name = name + ".off"
        self._save_off(file_name)

    def __str__(self):
        str = super(Grid, self).__str__() + " -> \n"
        for f_info in self.face_info:
            str += f_info.__str__() + "\n"
        return str

    class FaceInfo(object):
        def __init__(self, face_id,
                     top_vertex_info, left_vertex_info, right_vertex_info,
                     left_face_info, right_face_info, bottom_face_info):
            self.face_id = face_id

            self.top_vertex_info = top_vertex_info
            self.left_vertex_info = left_vertex_info
            self.right_vertex_info = right_vertex_info

            self.vertex_info = [top_vertex_info,
                                left_vertex_info,
                                right_vertex_info]

            self.left_face_info = left_face_info
            self.right_face_info = right_face_info
            self.bottom_face_info = bottom_face_info

        def __str__(self):
            str = super(Grid.FaceInfo, self).__str__() + "\n"
            for v_info in self.vertex_info:
                str += v_info.__str__() + "\n"
            return str

    class VertexInfo(object):
        """
        グリッド頂点情報クラス
        """

        def __init__(self, vertex_idx, face_id, alpha, beta):
            self.vertex_idx = vertex_idx
            self.face_id = face_id
            self.alpha = alpha
            self.beta = beta

        def __str__(self):
            return super(Grid.VertexInfo, self).__str__() + \
                   " -> idx : {}, face ID : {} alpha : {}, beta : {}".format(
                       self.vertex_idx, self.face_id, self.alpha, self.beta)
