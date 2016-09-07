#!/usr/bin/env python
# coding: utf-8

import enum
from src.util.debug_util import assert_type_in_container
from base_grid import BaseGrid, BaseFace


class TriangleGrid(BaseGrid):
    """

    正三角形の面を持つグリッドの基底クラス

    """

    def __init__(self, vertices, triangle_faces, n_face,
                 is_assertion_enabled=True):
        # assertion
        if is_assertion_enabled:
            assert_type_in_container(triangle_faces, TriangleFace)

        super(TriangleGrid, self).__init__(vertices, triangle_faces, n_face,
                                           is_assertion_enabled=False)


class TriangleFace(BaseFace):
    """

    TriangleGridの持つ面クラス

    """

    DIRECTION = enum.Enum('DIRECTION', 'HORIZON UPPER_RIGHT UPPER_LEFT')

    def __init__(self, face_id, n_div=1, vidx_table=None):
        """

        :type face_id: numbers.Integral
        :param face_id: 面を一意に識別するためのID

        :type n_div: numbers.Integral
        :param n_div: 面の分割数

        :type vidx_table: dict((float, float), numbers.Integral)
        :param vidx_table: 頂点座標(alpha, beta)と頂点インデックスのペア

        """
        super(TriangleFace, self).__init__(face_id, n_div, vidx_table)

    def set_vertex_idx(self, idx, alpha, beta):
        """

        頂点インデックスを登録する

        :type idx: int or long
        :param idx: 登録する頂点のインデックス

        :type alpha: int or long
        :param alpha: alpha座標

        :type beta: int or long
        :param beta: beta座標

        """

        assert isinstance(idx, (int, long)) and idx >= 0
        assert isinstance(alpha, (int, long)) and 0 <= alpha <= self.n_div
        assert isinstance(beta, (int, long)) and 0 <= beta <= self.n_div

        self.vidx_table[(alpha, beta)] = idx

    def get_vertex_idx(self, alpha, beta):
        """

        座標から頂点インデックスを取得する

        :type alpha: int or long
        :param alpha: alpha座標

        :type beta: int or long
        :param beta: beta座標

        :rtype: int or long
        :return: 頂点インデックス

        """
        return self.vidx_table[(alpha, beta)]

    def get_coordinates(self, vertex_idx):
        """

        頂点インデックスから座標を取得する

        :type vertex_idx: int or long
        :param vertex_idx: 頂点インデックス

        :rtype: tuple(int, int)
        :return: 面中における頂点座標

        """
        return [k for k, v in self.vidx_table.items() if v == vertex_idx]

    def vidx_table_as_copy(self):
        """

        自身の持つvidx_tableをコピーして返す

        :rtype: dict((int or long, int or long), int or long)
        :return: 頂点座標(alpha, beta)と頂点インデックスのペア

        """
        return dict(self.vidx_table)

    def top_vertex_idx(self):
        """

        面中のalpha=0,beta=0にある頂点インデックスを取得する

        :rtype: int
        :return: 頂点インデックス

        """
        return self.get_vertex_idx(0, 0)

    def left_vertex_idx(self):
        """

        面中のalpha=1,beta=0にある頂点インデックスを取得する

        :rtype: int
        :return: 頂点インデックス

        """
        return self.get_vertex_idx(self.n_div, 0)

    def right_vertex_idx(self):
        """

        面中のalpha=0,beta=1にある頂点インデックスを取得する

        :rtype: int
        :return: 頂点インデックス

        """
        return self.get_vertex_idx(0, self.n_div)

    def traverse(self, direction):
        """

        単一面の頂点インデックスを指定方向に走査し、入れ子リストとして返す

        :type direction: IcosahedronFace.DIRECTION
        :param direction: 操作方向の指定

        :rtype: list(list(int))
        :return: 頂点インデックスの入れ子リスト

        """

        coordinates = \
            {TriangleFace.DIRECTION.HORIZON: self.__horizon_coordinates,
             TriangleFace.DIRECTION.UPPER_RIGHT: self.__upper_right_coordinates,
             TriangleFace.DIRECTION.UPPER_LEFT: self.__upper_left_coordinates}[
                direction]

        return [[self.get_vertex_idx(alpha, beta)
                 for alpha, beta in zip(*coordinates(row))]
                for row in xrange(self.n_div + 1)]

    def __horizon_coordinates(self, row):
        """

        ある行で面上の頂点を水平にトラバースするときの順序に従った座標配列を返す

        :type row: int
        :param row: 現在注目している行

        :rtype: list(list(int), list(int))
        :return: alpha, betaの座標配列

        """
        alpha = xrange(row, -1, -1)
        beta = xrange(row + 1)
        return alpha, beta

    def __upper_right_coordinates(self, row):
        """

        ある行で面上の頂点を右上にトラバースするときの順序に従った座標配列を返す

        :type row: int
        :param row: 現在注目している行

        :rtype: list(list(int), list(int))
        :return: alpha, betaの座標配列

        """
        alpha = [self.n_div - row for i in xrange(row + 1)]
        beta = xrange(row, -1, -1)
        return alpha, beta

    def __upper_left_coordinates(self, row):
        """

        ある行で面上の頂点を左上にトラバースするときの順序に従った座標配列を返す

        :type row: int
        :param row: 現在注目している行

        :rtype: list(list(int), list(int))
        :return: alpha, betaの座標配列

        """
        alpha = xrange(row + 1)
        beta = [self.n_div - row for i in xrange(row + 1)]
        return alpha, beta

    def __str__(self):
        """

        :rtype: str
        :return: str化した時のTriangleFaceの文字列

        """
        s = super(TriangleFace, self).__str__() + \
            "vertex indices : (alpha, beta) -> [idx]\n"
        for key, idx in self.vertices_idx_dict.items():
            alpha, beta = key
            s += "({0:^3},{1:^3}) -> {2:^2}\n".format(alpha, beta, idx)
        return s
