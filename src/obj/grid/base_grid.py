#!/usr/bin/env python
# coding: utf-8

from collections import OrderedDict

import enum

from src.obj.obj3d import Obj3d
from src.util.debug_util import assert_type_in_container


class BaseGrid(Obj3d):
    """

    形状マップを生成するために使う、３次元空間上グリッドの基底クラス

    """
    BAND_TYPE = enum.Enum('BAND_TYPE', 'HORIZON UPPER_RIGHT LOWER_RIGHT')

    VERTEX_IDX_UNDEFINED = None

    def __init__(self, vertices, base_faces, n_face, n_div, upper_direction,
                 is_face_assertion_enabled=True):
        """

        :type vertices: np.ndarray
        :param vertices: 頂点座標配列

        :type base_faces: list(BaseFace) or tuple(BaseFace)
        :param base_faces: BaseFaceの集合

        :type n_face: int or long
        :param n_face: 面の数

        :type n_div: int or long
        :param n_div: 面の分割数

        :type is_face_assertion_enabled: bool
        :param is_face_assertion_enabled: メンバのアサーションチェックを有効にするかどうか

        :type upper_direction: (float, float, float)
        :param upper_direction: グリッドの上方向を表す単位ベクトル

        """

        super(BaseGrid, self).__init__(vertices)

        # assertion
        if is_face_assertion_enabled:
            assert_type_in_container(base_faces, BaseFace)
        assert isinstance(n_face, (int, long)) and n_face >= 0
        assert isinstance(n_div, (int, long)) and n_div > 0
        assert len(base_faces) == n_face

        self.grid_faces = base_faces
        self.n_face = n_face
        self.n_div = n_div
        self.upper_direction = upper_direction

    def traverse(self, uni_direction):
        """

        正二十面体グリッドの各面の頂点インデックスを走査し、
        結果をFaceIDとのペアで返す

        :type uni_direction: BaseFace.UNI_DIRECTION
        :param uni_direction: 走査方向

        :type is_upside_down: bool
        :param is_upside_down: 面が、グリッドの基準上方向ベクトルupper_direction
                               に対して上下逆さまかどうか

        :rtype dict
        :return FaceIDをキー、面の頂点インデックスリストをバリューとした辞書

        """
        return {
            grid_face.face_id: grid_face.traverse(uni_direction)
            for grid_face in self.grid_faces}

    def find_face_from_id(self, face_id):
        """

        指定したface_idを持つBaseFaceを返す
        指定したface_idを持つBaseFaceが見つからない場合、IndexErrorを投げる

        :type face_id: int
        :param face_id: 要求するBaseFaceのID

        :rtype: BaseFace
        :return: 指定したface_idを持つBaseFace

        """
        for grid_face in self.grid_faces:
            if grid_face.face_id == face_id:
                return grid_face
        else:
            raise IndexError

    def divide_face(self, n_div):
        raise NotImplementedError

    def __str__(self):
        """

        :rtype: str
        :return: str化した時のIcosahedronGridの文字列

        """
        s = super(BaseGrid, self).__str__() + "\n"
        for base_face in self.grid_faces:
            s += base_face.__str__() + "\n"
        return s


class BaseFace(object):
    """

    グリッドが持つ面の基底クラス

    """

    UNI_SCAN_DIRECTION = enum.Enum('UNI_DIRECTION',
                                   'HORIZON UPPER_RIGHT UPPER_LEFT \
                                    HORIZON_REVERSED UPPER_RIGHT_REVERSED \
                                    UPPER_LEFT_REVERSED')

    def __init__(self, face_id, n_div=1, vidx_table=None,
                 is_assertion_enabled=True):
        """

        :type face_id: int or long
        :param face_id: 面を一意に識別するためのID

        :type n_div: int or long
        :param n_div: 面の分割数

        :type vidx_table: dict((int or long, int or long), int or long)
        :param vidx_table: 頂点座標と頂点インデックスのペア

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
            s = s[:len(s) - 2] + " ) -> {:^2}\n".format(idx)
        return s

    def traverse(self, direction):
        raise NotImplementedError
