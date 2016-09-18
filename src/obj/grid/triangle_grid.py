#!/usr/bin/env python
# coding: utf-8

import numpy as np
from itertools import cycle
from src.util.debug_util import assert_type_in_container
from base_grid import BaseGrid, BaseFace


class TriangleGrid(BaseGrid):
    """

    正三角形の面を持つグリッドの基底クラス

    """

    def __init__(self, vertices, triangle_faces, n_face, n_div, upper_direction,
                 is_face_assertion_enabled=True):
        """

        :type vertices: np.ndarray
        :param vertices: 頂点座標配列

        :type triangle_faces: list(TriangleFace) or tuple(TriangleFace)
        :param triangle_faces: TriangleFaceの集合

        :type n_face: int or long
        :param n_face: 面の数

        :type n_div: int or long
        :param n_div: 面の分割数

        :type is_face_assertion_enabled: bool
        :param is_face_assertion_enabled: メンバのアサーションチェックを有効にするかどうか

        :type upper_direction: (float, float, float)
        :param upper_direction: グリッドの上方向を表す単位ベクトル

        """
        # assertion
        if is_face_assertion_enabled:
            assert_type_in_container(triangle_faces, TriangleFace)

        super(TriangleGrid, self).__init__(vertices, triangle_faces, n_face,
                                           n_div, upper_direction,
                                           is_face_assertion_enabled=False)

    def divide_face(self, n_div, epsilon=np.finfo(float).eps):
        """

        指定数で面を分割したGrid3dオブジェクトを返す

        :type n_div: int
        :param n_div: 分割数

        :type epsilon: float
        :param epsilon: 浮動小数点座標を等号比較する時の許容誤差

        :rtype : IcosahedronGrid
        :return : 分割後のGrid3dオブジェクト

        """

        new_vertices = np.empty(shape=(0, 3))

        new_grid_faces = []

        for grid_face in self.grid_faces:

            # グリッド面の三頂点
            top_vertex = self.vertices[grid_face.top_vertex_idx()]
            left_vertex = self.vertices[grid_face.left_vertex_idx()]
            right_vertex = self.vertices[grid_face.right_vertex_idx()]

            left_vector = left_vertex - top_vertex
            right_vector = right_vertex - top_vertex

            # 一旦GridFaceの頂点情報をクリア
            new_face = TriangleFace(grid_face.face_id,
                                    left_face_id=grid_face.left_face_id,
                                    right_face_id=grid_face.right_face_id,
                                    bottom_face_id=grid_face.bottom_face_id,
                                    n_div=n_div)

            for sum_length in xrange(n_div + 1):
                for i in xrange(sum_length + 1):
                    alpha = sum_length - i
                    beta = i
                    new_vertex = left_vector * float(
                        alpha) / n_div + right_vector * float(
                        beta) / n_div + top_vertex

                    # 重複チェック
                    check_duplicate = (
                        np.abs(new_vertex - new_vertices) < epsilon).all(axis=1)

                    if len(new_vertices) > 0 and check_duplicate.any():
                        v_idx = int(np.argwhere(check_duplicate)[0])
                    else:
                        v_idx = len(new_vertices)
                        new_vertices = np.vstack((new_vertices, new_vertex))

                    # 新しく頂点情報を追加
                    new_face.set_vertex_idx(v_idx, alpha, beta)

            new_grid_faces.append(new_face)

        return TriangleGrid(new_vertices, new_grid_faces, self.n_face,
                            n_div, self.upper_direction)

    def traverse_band(self, band_type, center_face_id):
        """

        帯状にグリッド上の頂点を走査し、走査順に頂点インデックスを返す
        頂点インデックスはself.verticesに対応する

        :type band_type: BaseGrid.BAND_TYPE
        :param band_type: 帯の走査方向

        :type center_face_id: int or long
        :param center_face_id: 帯の中心となる面のID

        :rtype: list(list)
        :return: 走査順にソートされた頂点のインデックス

        """
        if band_type == BaseGrid.BAND_TYPE.HORIZON:
            direction_loop = cycle(
                (BaseFace.UNI_SCAN_DIRECTION.HORIZON,
                 BaseFace.UNI_SCAN_DIRECTION.HORIZON_REVERSED))
            next_fid_func_loop = cycle((lambda face: face.right_face_id,
                                        lambda face: face.left_face_id))
        elif band_type == BaseGrid.BAND_TYPE.UPPER_RIGHT:
            direction_loop = cycle(
                (BaseFace.UNI_SCAN_DIRECTION.UPPER_LEFT_REVERSED,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_LEFT,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_LEFT_REVERSED,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_LEFT,
                 BaseFace.UNI_SCAN_DIRECTION.HORIZON_REVERSED,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_RIGHT,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_RIGHT_REVERSED,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_LEFT,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_LEFT_REVERSED,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_LEFT))
            next_fid_func_loop = cycle((lambda face: face.right_face_id,
                                        lambda face: face.bottom_face_id,
                                        lambda face: face.right_face_id,
                                        lambda face: face.bottom_face_id,
                                        lambda face: face.left_face_id,
                                        lambda face: face.left_face_id,
                                        lambda face: face.bottom_face_id,
                                        lambda face: face.bottom_face_id,
                                        lambda face: face.right_face_id,
                                        lambda face: face.bottom_face_id))
        elif band_type == BaseGrid.BAND_TYPE.LOWER_RIGHT:
            direction_loop = cycle(
                (BaseFace.UNI_SCAN_DIRECTION.UPPER_RIGHT_REVERSED,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_RIGHT,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_RIGHT_REVERSED,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_RIGHT,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_LEFT_REVERSED,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_LEFT,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_RIGHT_REVERSED,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_RIGHT,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_RIGHT_REVERSED,
                 BaseFace.UNI_SCAN_DIRECTION.UPPER_RIGHT))
            next_fid_func_loop = cycle((lambda face: face.bottom_face_id,
                                        lambda face: face.left_face_id,
                                        lambda face: face.bottom_face_id,
                                        lambda face: face.left_face_id,
                                        lambda face: face.right_face_id,
                                        lambda face: face.bottom_face_id,
                                        lambda face: face.bottom_face_id,
                                        lambda face: face.left_face_id,
                                        lambda face: face.bottom_face_id,
                                        lambda face: face.left_face_id))
        else:
            raise NotImplementedError

        result = [[] for _ in xrange(self.n_div + 1)]

        face_id = center_face_id
        while True:
            direction = direction_loop.next()
            face = self.find_face_from_id(face_id)
            traversed_rows = face.traverse(direction)
            for result_row, traversed_row in zip(result, traversed_rows):
                # 重複を防ぐため、先頭要素は飛ばす
                result_row += traversed_row[1:]
            face_id = next_fid_func_loop.next()(face)

            if face_id == center_face_id:
                break

        return result


class TriangleFace(BaseFace):
    """

    TriangleGridの持つ面クラス

    """

    def __init__(self, face_id, left_face_id, right_face_id, bottom_face_id,
                 n_div=1, vidx_table=None):
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
        super(TriangleFace, self).__init__(face_id, n_div, vidx_table)
        self.left_face_id = left_face_id
        self.right_face_id = right_face_id
        self.bottom_face_id = bottom_face_id

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

        :type direction: icosahedronface.direction
        :param direction: 操作方向の指定

        :rtype: list(list(int))
        :return: 頂点インデックスの入れ子リスト

        """
        if direction == TriangleFace.UNI_SCAN_DIRECTION.HORIZON:
            coordinates = self.__horizon_row_coordinates
            is_reversed = False
        elif direction == TriangleFace.UNI_SCAN_DIRECTION.UPPER_RIGHT:
            coordinates = self.__upper_right_row_coordinates
            is_reversed = False
        elif direction == TriangleFace.UNI_SCAN_DIRECTION.UPPER_LEFT:
            coordinates = self.__upper_left_row_coordinates
            is_reversed = False
        elif direction == TriangleFace.UNI_SCAN_DIRECTION.HORIZON_REVERSED:
            coordinates = self.__horizon_row_coordinates
            is_reversed = True
        elif direction == TriangleFace.UNI_SCAN_DIRECTION.UPPER_RIGHT_REVERSED:
            coordinates = self.__upper_right_row_coordinates
            is_reversed = True
        elif direction == TriangleFace.UNI_SCAN_DIRECTION.UPPER_LEFT_REVERSED:
            coordinates = self.__upper_left_row_coordinates
            is_reversed = True
        else:
            raise KeyError

        rows = xrange(self.n_div, -1, -1) if is_reversed \
            else xrange(self.n_div + 1)

        return [[self.get_vertex_idx(alpha, beta)
                 for alpha, beta in zip(*coordinates(row, is_reversed))]
                for row in rows]

    def __horizon_row_coordinates(self, row, is_reversed):
        """

        ある行で面上の頂点を水平にトラバースするときの順序に従った座標配列を返す

        :type row: int
        :param row: 現在注目している行

        :type is_reversed: bool
        :param is_reversed: 面が、グリッドの基準上方向ベクトルupper_direction
                               に対して上下逆さまかどうか

        :rtype: list(list(int), list(int))
        :return: alpha, betaの座標配列

        """

        alpha = xrange(row, -1, -1)
        beta = xrange(row + 1)
        if is_reversed:
            alpha = reversed(list(alpha))
            beta = reversed(list(beta))
        return alpha, beta

    def __upper_right_row_coordinates(self, row, is_reversed):
        """

        ある行で面上の頂点を右上にトラバースするときの順序に従った座標配列を返す

        :type row: int
        :param row: 現在注目している行

        :type is_reversed: bool
        :param is_reversed: 面が、グリッドの基準上方向ベクトルupper_direction
                               に対して上下逆さまかどうか

        :rtype: list(list(int), list(int))
        :return: alpha, betaの座標配列

        """

        alpha = [self.n_div - row for i in xrange(row + 1)]
        beta = xrange(row, -1, -1)
        if is_reversed:
            alpha = reversed(alpha)
            beta = reversed(list(beta))
        return alpha, beta

    def __upper_left_row_coordinates(self, row, is_reversed):
        """

        ある行で面上の頂点を左上にトラバースするときの順序に従った座標配列を返す

        :type row: int
        :param row: 現在注目している行

        :type is_reversed: bool
        :param is_reversed: 面が、グリッドの基準上方向ベクトルupper_direction
                               に対して上下逆さまかどうか

        :rtype: list(list(int), list(int))
        :return: alpha, betaの座標配列

        """
        alpha = xrange(row + 1)
        beta = [self.n_div - row for _ in xrange(row + 1)]
        if is_reversed:
            alpha = reversed(list(alpha))
            beta = reversed(beta)
        return alpha, beta
