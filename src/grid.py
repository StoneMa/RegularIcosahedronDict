#!/usr/bin/env python
# coding: utf-8


import os


class IcoGrid(object):
    """
    距離マップ生成用グリッドクラス
    """

    def __init__(self, grd_file):

        if os.path.splitext(grd_file)[-1] != ".grd":
            raise IOError(
                "IcoGrid::__init__ : file path is incorrect : {}".format(
                    grd_file))

        faces = []

        with open(grd_file) as f:
            lines = filter(lambda x: len(x) > 0 and x[0] != "#",
                           [line.strip().split() for line in f.readlines()])

            vertices = [list(map(float, line[1:])) for line in lines if
                        line[0] == 'v']

            face_vertices = [list(map(int, line[1:])) for line in lines if
                             line[0] == 'f']

            adjacent_faces = [list(map(int, line[2:])) for line in lines if
                              line[0] == 'af']

            for i, fv in enumerate(face_vertices):
                xyz_top = vertices[fv[0]]
                xyz_left = vertices[fv[1]]
                xyz_right = vertices[fv[2]]

                p_top = IcoGrid.Point(xyz_top[0], xyz_top[1], xyz_top[2],
                                      alpha=0, beta=0)
                p_left = IcoGrid.Point(xyz_left[0], xyz_left[1], xyz_left[2],
                                       alpha=1, beta=0)
                p_right = IcoGrid.Point(xyz_right[0], xyz_right[1],
                                        xyz_right[2], alpha=0, beta=1)

                faces.append(IcoGrid.Face(i, p_top, p_left, p_right))

            for face, af in zip(faces, adjacent_faces):
                id_left, id_right, id_bottom = af
                face.left_face = faces[id_left]
                face.right_face = faces[id_right]
                face.bottom_face = faces[id_bottom]

        self.faces = faces

    class Face(object):
        """
        グリッド面
        """

        def __init__(self, face_id, point_top, point_left, point_right,
                     left_face=None, right_face=None, bottom_face=None):
            self.face_id = face_id

            # ３頂点
            assert isinstance(point_top, IcoGrid.Point)
            assert isinstance(point_left, IcoGrid.Point)
            assert isinstance(point_right, IcoGrid.Point)
            self.point_top = point_top
            self.point_left = point_left
            self.point_right = point_right

            # 隣接３平面
            assert isinstance(left_face, IcoGrid.Face) or left_face is None
            assert isinstance(right_face, IcoGrid.Face) or right_face is None
            assert isinstance(bottom_face, IcoGrid.Face) or bottom_face is None
            self.left_face = left_face
            self.right_face = right_face
            self.bottom_face = bottom_face

            # 平面上のグリッド頂点集合
            self.points = [point_top, point_left, point_right]

    class Point(object):
        """
        グリッド頂点
        """

        def __init__(self, x, y, z, alpha, beta):
            self.x = x
            self.y = y
            self.z = z
            self.alpha = alpha
            self.beta = beta

        def __str__(self):
            str = super(IcoGrid.Point, self).__str__()
            str += " -> x : {}, y : {}, z : {}, alpha : {}, beta : {}".format(
                self.x, self.y, self.z, self.alpha, self.beta)
            return str


if __name__ == '__main__':
    for face in IcoGrid('../res/new_regular_ico.grd').faces:
        for p in face.points:
            print p
