#!/usr/bin/env python
# coding: utf-8


import os
import numpy as np


class Grid(object):
    """
    距離マップ生成用グリッドクラス
    """

    def __init__(self, grd_file):

        if os.path.splitext(grd_file)[-1] != ".grd":
            raise IOError(
                "IcoGrid::__init__ : file path is incorrect : {}".format(
                    grd_file))

        vertices = []
        face_vertices = []
        adjacent_faces = []

        self.faces = []

        with open(grd_file) as f:

            for line in f.readlines():

                line = line.strip().split()

                if len(line) == 0 or line[0] == '#':
                    continue

                if line[0] == 'v':
                    vertices.append(np.array(map(float, line[1:])))

                if line[0] == 'f':
                    face_vertices.append(np.array(map(int, line[1:])))

                if line[0] == 'af':
                    adjacent_faces.append(np.array(map(int, line[2:])))

            for face_id, fv in enumerate(face_vertices):
                grid_face = Grid.GridFace(face_id,
                                          Grid.GridPoint(vertices[fv[0]], 0, 0),
                                          Grid.GridPoint(vertices[fv[1]], 1, 0),
                                          Grid.GridPoint(vertices[fv[2]], 0, 1))
                self.faces.append(grid_face)

            for face, af in zip(self.faces, adjacent_faces):
                id_left, id_right, id_bottom = af
                face.left_face = self.faces[id_left]
                face.right_face = self.faces[id_right]
                face.bottom_face = self.faces[id_bottom]

    def divide_face(self, n_div):

        for face in self.faces:
            new_points = []
            left_vector = face.point_left.xyz - face.point_top.xyz
            right_vector = face.point_right.xyz - face.point_top.xyz

            for sum_length in xrange(n_div + 1):
                for i in xrange(sum_length + 1):
                    alpha = float(sum_length - i) / n_div
                    beta = float(i) / n_div
                    new_xyz = left_vector * alpha + right_vector * beta + face.point_top.xyz
                    new_points.append(Grid.GridPoint(new_xyz, alpha, beta))

            face.points = new_points

    def save_obj(self, obj_file):

        name, ext = os.path.splitext(obj_file)
        if ext != ".obj" or ext == "":
            obj_file = name + ".obj"

        with open(obj_file, "w") as f:

            # 頂点座標
            vertices = np.array(
                [p.xyz for face in self.faces for p in face.points])

            # OBJファイル先頭行コメント
            f.write("# OBJ file format with ext .obj\n")
            f.write("# vertex count = {}\n".format(len(vertices)))
            f.write("# face count = {}\n".format(len(self.faces)))

            # 頂点情報
            for x, y, z in vertices:
                f.write("v {0:10f} {1:10f} {2:10f}\n".format(x, y, z))

    def __str__(self):
        str = super(Grid, self).__str__() + " -> \n"
        for face in self.faces:
            str += face.__str__() + "\n"
        return str

    class GridFace(object):
        """
        グリッド面
        """

        def __init__(self, face_id, point_top, point_left, point_right,
                     left_face=None, right_face=None, bottom_face=None):
            self.face_id = face_id

            # ３頂点
            assert isinstance(point_top, Grid.GridPoint)
            assert isinstance(point_left, Grid.GridPoint)
            assert isinstance(point_right, Grid.GridPoint)
            self.point_top = point_top
            self.point_left = point_left
            self.point_right = point_right

            # 隣接３平面
            assert isinstance(left_face, Grid.GridFace) or left_face is None
            assert isinstance(right_face, Grid.GridFace) or right_face is None
            assert isinstance(bottom_face, Grid.GridFace) or bottom_face is None
            self.left_face = left_face
            self.right_face = right_face
            self.bottom_face = bottom_face

            # 平面上のグリッド頂点集合
            self.points = [point_top, point_left, point_right]

        def __str__(self):
            str = super(Grid.GridFace, self).__str__()
            str += " -> Face ID : {}\n".format(self.face_id)
            for p in self.points:
                str += p.__str__() + "\n"
            str += "Left Face : {}, Right Face : {}, Bottom Face : {}\n".format(
                self.left_face.face_id, self.right_face.face_id,
                self.bottom_face.face_id)
            return str

    class GridPoint(object):
        """
        グリッド頂点
        """

        def __init__(self, xyz, alpha, beta):
            assert hasattr(xyz, "__getitem__") and len(xyz) == 3
            self.xyz = np.asarray(xyz)
            self.alpha = alpha
            self.beta = beta

        def __str__(self):
            self_x, self_y, self_z = self.xyz
            return super(Grid.GridPoint, self).__str__() + \
                   " -> x : {0:<13}, y : {1:<13}, z : {2:<13}, alpha : {3}, beta : {4}".format(
                       self_x, self_y, self_z, self.alpha, self.beta)
