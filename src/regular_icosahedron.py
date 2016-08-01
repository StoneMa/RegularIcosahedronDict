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
    def load(path):
        """

        ファイルパスの拡張子を識別して読み込みを行い、RegularIcosahedronオブジェクトを返す

        :type path: str
        :param path: ファイルパス

        :rtype: RegularIcosahedron
        :return: RegularIcosahedronオブジェクト

        """
        model = Model.load(path)
        return RegularIcosahedron(model.vertices, model.normals, model.faces,
                                  model.file_type)

    @staticmethod
    def division(n, regular_icosahedron):
        """

        面をn分割したRegularIcosahedronオブジェクトを返戻する
        返戻されるRegularIcosahedronの頂点情報は z成分→角度 の優先度でソートされる
        ただし、面情報は破棄される

        :type n: int
        :param n: 面の分割数

        :type regular_icosahedron: RegularIcosahedron
        :param regular_icosahedron: RegularIcosahedronオブジェクト

        :rtype: RegularIcosahedron
        :return: 頂点情報のみの分割後RegularIcosahedronオブジェクト

        """

        # 面をn分割
        for i in xrange(n):
            RegularIcosahedron.__division_ignore_order(regular_icosahedron)

        # 重複した頂点を排除
        vertices = list(set(map(tuple, regular_icosahedron.vertices)))

        # z成分とxyのなす角度のペアのリスト
        values = [(z, np.arctan2(x, y)) for x, y, z in vertices]

        # z成分→角度の優先度でインデックスをソート
        dtype = [('z', float), ('angle', float)]
        angle_z = np.array(values, dtype=dtype)

        # ソート済み頂点配列
        arg_vertices = np.argsort(angle_z, axis=0, order=('z', 'angle'))

        return RegularIcosahedron(np.array(vertices)[arg_vertices][::-1], None,
                                  None, regular_icosahedron.file_type)

    @staticmethod
    def __division_ignore_order(regular_icosahedron):
        """

        RegularIcosahedronの三角面を４つに分割する
        返戻される頂点リストは順序を考慮していない
        面情報も順序を考慮してしないが、正三角形を構成する３点の順序は保持される

        :type regular_icosahedron: RegularIcosahedron
        :param regular_icosahedron: RegularIcosahedronオブジェクト

        """
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
    ico = RegularIcosahedron.load("../res/regular_icosahedron.obj")
    print "ico.vertices : ", ico.vertices.shape
    ico = RegularIcosahedron.division(3, ico)
    print "ico.vertices : ", ico.vertices.shape
    print ico.vertices
    ico.save("ico4.obj")
