#!/usr/bin/env python
# coding: utf-8

"""

regular_icosahedron.py

正二十面体モデルを定義するモジュール

"""

import numpy as np
from model import Model


class RegularIcosahedron(Model):
    """
    正二十面体モデルクラス
    """

    def __init__(self, vertices, normals, faces, file_type):
        super(RegularIcosahedron, self).__init__(vertices, normals, faces,
                                                 file_type)

    @staticmethod
    def load_obj(obj_file):
        model = Model.load_obj(obj_file)
        return RegularIcosahedron(model.vertices, model.normals, model.faces,
                                  model.file_type)

    @staticmethod
    def load_off(off_file):
        model = Model.load_off(off_file)
        return RegularIcosahedron(model.vertices, model.normals, model.faces,
                                  model.file_type)

    @staticmethod
    def division(regular_icosahedron):
        if not isinstance(regular_icosahedron, RegularIcosahedron):
            raise TypeError("RegularIcosahedron::division()")

        # divisionは数回しか呼ばれないので、appendで済ます
        new_vertices = []
        new_faces = []
        for f in regular_icosahedron.faces:
            # faceを構成する3点
            p1, p2, p3 = regular_icosahedron.vertices[f]

            # 新しい中点
            p4 = p1 * 0.5 + p2 * 0.5
            p5 = p2 * 0.5 + p3 * 0.5
            p6 = p3 * 0.5 + p1 * 0.5

            # 新しいface情報
            head = len(new_vertices)
            f1 = [head + 0, head + 3, head + 5]
            f2 = [head + 3, head + 1, head + 4]
            f3 = [head + 5, head + 4, head + 2]
            f4 = [head + 3, head + 4, head + 5]

            new_vertices.extend([p1, p2, p3, p4, p5, p6])
            new_faces.extend([f1, f2, f3, f4])

        regular_icosahedron.vertices = np.array(new_vertices)
        regular_icosahedron.faces = np.array(new_faces)


if __name__ == '__main__':
    ico = RegularIcosahedron.load_obj("../res/regular_icosahedron.obj")
    print "ico.vertices : ", ico.vertices.shape
    RegularIcosahedron.division(ico)
    print "ico.vertices : ", ico.vertices.shape
    RegularIcosahedron.division(ico)
    print "ico.vertices : ", ico.vertices.shape

    ico.save("../res/ico.obj")
