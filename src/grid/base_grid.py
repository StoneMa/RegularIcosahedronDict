#!/usr/bin/env python
# coding: utf-8

from collections import OrderedDict
from src.obj3d import Obj3d
from src.util.debug_util import assert_type_in_container


class BaseGrid(Obj3d):
    """

    形状マップを生成するために使う、３次元空間上グリッドの基底クラス

    """

    def __init__(self, vertices, base_faces, n_face, is_assertion_enabled=True):
        """

        :type vertices: np.ndarray
        :param vertices: 頂点座標配列

        :type base_faces: list(BaseFace) or tuple(BaseFace)
        :param base_faces: BaseFaceの集合

        :type n_face: int or long
        :param n_face: 面の数

        :type is_assertion_enabled: bool
        :param is_assertion_enabled: メンバのアサーションチェックを有効にするかどうか

        """

        super(BaseGrid, self).__init__(vertices)

        # assertion
        if is_assertion_enabled:
            assert_type_in_container(base_faces, BaseFace)
            assert isinstance(n_face, (int, long)) and n_face >= 0

        self.base_faces = base_faces
        self.n_face = n_face

    def __str__(self):
        """

        :rtype: str
        :return: str化した時のIcosahedronGridの文字列

        """
        s = super(BaseGrid, self).__str__() + "\n"
        for base_face in self.base_faces:
            s += base_face.__str__() + "\n"
        return s


class BaseFace(object):
    """

    グリッドが持つ面の基底クラス

    """

    def __init__(self, face_id, n_div=1, vidx_table=None,
                 is_assertion_enabled=True):
        """

        :type face_id: int or long
        :param face_id: 面を一意に識別するためのID

        :type n_div: int or long
        :param n_div: 面の分割数

        :type vidx_table: dict((int or long, int or long), int or long)
        :param vidx_table: 頂点座標(alpha, beta)と頂点インデックスのペア

        :type is_assertion_enabled: bool
        :param is_assertion_enabled: メンバのアサーションチェックを有効にするかどうか

        """

        # assertion
        if is_assertion_enabled:
            assert isinstance(face_id, (int, long)) and face_id >= 0
            assert isinstance(n_div, (int, long)) and n_div >= 0
            assert isinstance(vidx_table, dict) or vidx_table is None

        self.face_id = face_id
        self.n_div = n_div
        self.vidx_table = OrderedDict() if vidx_table is None else vidx_table

    def __str__(self):
        """

        :rtype: str
        :return: str化した時のBaseFaceの文字列

        """
        s = "face ID : {} (n_div = {})\n".format(self.face_id, self.n_div) + \
            "vertex indices : ( coordinates ... ) -> [ idx ]\n"
        for coordinates, idx in self.vidx_table.items():
            s += "("
            for coordinate in coordinates:
                s += "{:^3},".format(coordinate)
            s = s[:len(s)-2] + " ) -> {:^2}\n".format(idx)
        return s
