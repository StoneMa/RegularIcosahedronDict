#!/usr/bin/env python
# coding: utf-8

from base_grid import BaseGrid, BaseFace
from src.util.debug_util import assert_type_in_container


class SquareGrid(BaseGrid):
    """

    正四角形の面を持つグリッドの基底クラス

    """

    def __init__(self, vertices, square_faces, n_face, n_div, upper_direction,
                 is_face_assertion_enabled=True):
        """

        :type vertices: np.ndarray
        :param vertices: 頂点座標配列

        :type square_faces: list(SquareFaces) or tuple(SquareFaces)
        :param square_faces: SquareFacesの集合

        :type n_face: int or long
        :param n_face: 面の数

        :type n_div: int or long
        :param n_div: 面の分割数

        :type upper_direction: (float, float, float)
        :param upper_direction: グリッドの上方向を表す単位ベクトル

        :type is_face_assertion_enabled: bool
        :param is_face_assertion_enabled: メンバのアサーションチェックを有効にするかどうか

        """
        # assertion
        if is_face_assertion_enabled:
            assert_type_in_container(square_faces, SquareFace)

        super(SquareGrid, self).__init__(vertices, square_faces, n_face, n_div,
                                         upper_direction,
                                         is_face_assertion_enabled=False)

    def divide_face(self, n_div):
        """

        指定数で面を分割したSquareGridオブジェクトを返す

        :type n_div: int
        :param n_div: 分割する

        :rtype:
        :return:

        """
        pass



class SquareFace(BaseFace):
    """

    SquareGridが持つ面クラス

    """

    def __init__(self, face_id, top_face_id, left_face_id, right_face_id,
                 bottom_face_id, n_div=1, vidx_table=None):
        """

        :type face_id: int or long
        :param face_id: 面を一意に識別するためのID

        :type left_face_id: int or long
        :param left_face_id: 左辺に隣接するface_id

        :type right_face_id: int or long
        :param right_face_id: 右辺に隣接するface_id

        :type bottom_face_id: int or long
        :param bottom_face_id: 底辺に隣接するface_id

        :type n_div: int or long
        :param n_div: 面の分割数

        :type vidx_table: dict((int or long, int or long), int or long)
        :param vidx_table: 頂点座標(alpha, beta)と頂点インデックスのペア

        """

        super(SquareFace, self).__init__(face_id, n_div, vidx_table)
