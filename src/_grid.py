#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
from collections import OrderedDict
from src._obj3d import _Obj3d


class Grid3d(_Obj3d):
    """
    距離マップ生成用グリッドクラス
    face情報・normal情報は失われる
    代わりに各グリッド面の情報GridFaceが保持される
    """

    VERTEX_IDX_UNDEFINED = None

    TRAVERSED_ORDER_HORIZON = "TRAVERSED_ORDER_HORIZON"
    TRAVERSED_ORDER_TO_LOWER_RIGHT = "TRAVERSED_ORDER_TO_LOWER_RIGHT"
    TRAVERSED_ORDER_TO_UPPER_RIGHT = "TRAVERSED_ORDER_TO_UPPER_RIGHT"

    def __init__(self, vertices, grid_faces, n_div, traversed_order):
        """

        :type vertices: list or tuple or np.ndarray
        :param vertices: 全頂点情報

        :type grid_faces: list or tuple
        :param grid_faces: 多角形グリッドの各面の情報

        :type n_div: int
        :param n_div: Grid3dオブジェクトの各面の分割数

        """
        super(Grid3d, self).__init__(vertices)
        self.grid_faces = tuple(grid_faces)
        self.n_div = n_div
        self.traversed_order = traversed_order

    @staticmethod
    def load(grd_file):
        """

        .grd形式のファイルを読み込み、Grid3dオブジェクトを返す

        :type grd_file: str
        :param grd_file: .grd形式のファイルパス

        :rtype : Grid3d
        :return : Grid3dオブジェクト
        """

        if os.path.splitext(grd_file)[-1] != ".grd":
            raise IOError(
                "IcoGrid::__init__ : file path is incorrect : {}".format(
                    grd_file))

        vertices = []
        face_vertices = []
        adjacent_faces = []
        traversed_order = {}

        with open(grd_file) as f:

            for line in f.readlines():

                line = line.strip().split()

                if len(line) == 0 or line[0] == '#':
                    continue

                if line[0] == 'v':
                    vertices.append(map(float, line[1:]))

                elif line[0] == 'f':
                    face_vertices.append(map(int, line[1:]))

                elif line[0] == 'af':
                    adjacent_faces.append(map(int, line[1:]))

                elif line[0] == 'to':
                    if line[1] == 'h':
                        key = Grid3d.TRAVERSED_ORDER_HORIZON
                    elif line[1] == 'l':
                        key = Grid3d.TRAVERSED_ORDER_TO_LOWER_RIGHT
                    elif line[1] == 'u':
                        key = Grid3d.TRAVERSED_ORDER_TO_UPPER_RIGHT

                    traversed_order[key] = list(map(int, line[2:]))

                    vertices = np.asarray(vertices)

                    grid_faces = np.array([GridFace(face_id, None, None, None)
                                           for face_id, fv in
                                           enumerate(face_vertices)])

                    for grid_face, fv, af in zip(grid_faces, face_vertices,
                                                 adjacent_faces):
                        # 面を構成する三頂点の追加
                        top_vertex_idx, left_vertex_idx, right_vertex_idx = fv
                        grid_face.set_vertex_idx(idx=top_vertex_idx, alpha=0,
                                                 beta=0)
                        grid_face.set_vertex_idx(idx=left_vertex_idx, alpha=1,
                                                 beta=0)
                        grid_face.set_vertex_idx(idx=right_vertex_idx, alpha=0,
                                                 beta=1)

                        # 隣接する三つの面の追加
                        left_face, right_face, bottom_face = grid_faces[af]
                        grid_face.left_face = left_face
                        grid_face.right_face = right_face
                        grid_face.bottom_face = bottom_face

        return Grid3d(vertices, grid_faces, 1, dict(traversed_order))

    def divide_face(self, n_div, epsilon=np.finfo(float).eps):
        """

        指定数で面を分割したGrid3dオブジェクトを返す

        :type n_div: int
        :param n_div: 分割数

        :type epsilon: float
        :param epsilon: 浮動小数点座標を等号比較する時の許容誤差

        :rtype : Grid3d
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
            new_face = GridFace(grid_face.face_id, None, None, None)

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
                        v_idx = int(np.argwhere(check_duplicate))
                    else:
                        v_idx = len(new_vertices)
                        new_vertices = np.vstack((new_vertices, new_vertex))

                    # 新しく頂点情報を追加
                    new_face.set_vertex_idx(v_idx, alpha, beta)

            new_grid_faces.append(new_face)

        # 新しいGridFaceのleft_face,right_face,bottom_faceをセットする
        for new_face, old_face in zip(new_grid_faces, self.grid_faces):
            new_face.left_face = self.find_face_from_id(
                old_face.left_face.face_id)
            new_face.right_face = self.find_face_from_id(
                old_face.right_face.face_id)
            new_face.bottom_face = self.find_face_from_id(
                old_face.bottom_face.face_id)

        return Grid3d(new_vertices, new_grid_faces, n_div, self.traversed_order)

    def find_face_from_id(self, face_id):
        """

        指定したface_idを持つGridFaceを返す
        指定したface_idを持つGridFaceが見つからない場合、IndexErrorを投げる

        :type face_id: int
        :param face_id: 要求するGridFaceのID

        :rtype: GridFace
        :return: 指定したface_idを持つGridFace

        """
        for grid_face in self.grid_faces:
            if grid_face.face_id == face_id:
                return grid_face
        else:
            raise IndexError

    def traverse(self):
        """

        グリッドの各帯に対応する頂点インデックス配列を返す

        :type center_grid_face: GridFace
        :param center_grid_face: 帯の中心とするGridFace

        :rtype: list of np.ndarray
        :return: グリッドの各帯に対応する頂点インデックス配列

        """

        def get_horizon_alpha_array(row, is_face_upward):
            if is_face_upward:
                return xrange(row, -1, -1)
            else:
                return xrange(self.n_div - row + 1)

        def get_lower_right_alpha_array(row, is_face_upward):
            if is_face_upward:
                return [row for i in xrange(self.n_div - row + 1)]
            else:
                return [self.n_div - row for i in xrange(row + 1)]

        def get_upper_right_alpha_array(row, is_face_upward):
            if is_face_upward:
                return xrange(self.n_div - row, -1, -1)
            else:
                return xrange(row + 1)

        def get_horizon_beta_array(row, is_face_upward):
            if is_face_upward:
                return xrange(row + 1)
            else:
                return xrange(self.n_div - row, -1, -1)

        def get_lower_right_beta_array(row, is_face_upward):
            if is_face_upward:
                return xrange(self.n_div - row + 1)
            else:
                return xrange(row, -1, -1)

        def get_upper_right_beta_array(row, is_face_upward):
            if is_face_upward:
                return [row for i in xrange(self.n_div - row + 1)]
            else:
                return [self.n_div - row for i in xrange(row + 1)]

        horizon = self.__traverse(
            traversed_order_key=Grid3d.TRAVERSED_ORDER_HORIZON,
            get_init_row_size=lambda x: self.n_div - x,
            get_alpha_array=get_horizon_alpha_array,
            get_beta_array=get_horizon_beta_array)

        to_lower_right = self.__traverse(
            traversed_order_key=Grid3d.TRAVERSED_ORDER_TO_LOWER_RIGHT,
            get_init_row_size=lambda x: x,
            get_alpha_array=get_lower_right_alpha_array,
            get_beta_array=get_lower_right_beta_array)

        to_uoper_right = self.__traverse(
            traversed_order_key=Grid3d.TRAVERSED_ORDER_TO_UPPER_RIGHT,
            get_init_row_size=lambda x: self.n_div - x,
            get_alpha_array=get_upper_right_alpha_array,
            get_beta_array=get_upper_right_beta_array)

        return horizon, to_lower_right, to_uoper_right

    def __traverse(self, traversed_order_key, get_init_row_size,
                   get_alpha_array, get_beta_array):
        """

        グリッド頂点を帯状に走査し、頂点インデックス配列を返す

        :type center_grid_face: GridFace
        :param center_grid_face: 帯の中心とするGridFace

        :type first_grid_face_attr: str
        :param first_grid_face_attr: 面走査時、一番目に移動する面のメンバ名

        :type second_grid_face_attr: str
        :param second_grid_face_attr: 面走査時、一番目に移動する面のメンバ名

        :type get_init_row_size: int()
        :param get_init_row_size: 各vertex_rowの初期サイズを返す関数

        :type get_alpha_beta: tuple()
        :param get_alpha_beta: alpha, betaの組を返す関数

        :rtype : np.ndarray
        :return: 頂点インデックス配列

        """

        # 面一周分のリスト
        traversed_grid_faces = [self.find_face_from_id(face_id) for face_id in
                                self.traversed_order[traversed_order_key]]

        vertex_indices = []

        # 指定した方向へ頂点走査を行う
        # rowは、帯の行を表す
        for row in xrange(self.n_div + 1):

            # 各行の先頭に、頂点インデックス未定義要素が入る
            indices_row = [Grid3d.VERTEX_IDX_UNDEFINED] * get_init_row_size(row)

            for traversed_face_idx, traversed_face in enumerate(
                    traversed_grid_faces):
                is_triangle_upward = traversed_face_idx % 2 == 0
                alpha_array = list(get_alpha_array(row, is_triangle_upward))
                beta_array = list(get_beta_array(row, is_triangle_upward))
                # 頂点の重複を防ぐため、最後の面以外では、最後の頂点は無視する
                if traversed_face_idx < len(traversed_grid_faces) - 1:
                    alpha_array = alpha_array[:len(alpha_array) - 1]
                    beta_array = beta_array[:len(beta_array) - 1]
                for alpha, beta in zip(alpha_array, beta_array):
                    indices_row.append(
                        traversed_face.get_vertex_idx(alpha, beta))

            # 距離マップの後ろにパディングを追加
            indices_row += [Grid3d.VERTEX_IDX_UNDEFINED] * (
                self.n_div - get_init_row_size(row))
            # 一行分のインデックスをlistとして格納
            vertex_indices.append(indices_row)

        return np.asarray(vertex_indices)

    def center(self):
        obj3d = super(Grid3d, self).center()
        return Grid3d(obj3d.vertices, self.grid_faces_as_copy(), self.n_div,
                      self.traversed_order_as_copy())

    def normal(self):
        obj3d = super(Grid3d, self).normal()
        return Grid3d(obj3d.vertices, self.grid_faces_as_copy(), self.n_div,
                      self.traversed_order_as_copy())

    def scale(self, r):
        obj3d = super(Grid3d, self).scale(r)
        return Grid3d(obj3d.vertices, self.grid_faces_as_copy(), self.n_div,
                      self.traversed_order_as_copy())

    def grid_faces_as_copy(self):
        new_grid_faces = [
            GridFace(gf.face_id, None, None, None, gf.vertices_idx_as_copy())
            for gf in self.grid_faces]

        def find_face_from_id(face_id):
            for new_grid_face in new_grid_faces:
                if new_grid_face.face_id == face_id:
                    return new_grid_face
            else:
                raise IndexError

        for new_face, old_face in zip(new_grid_faces, self.grid_faces):
            new_face.left_face = find_face_from_id(old_face.left_face.face_id)
            new_face.right_face = find_face_from_id(old_face.right_face.face_id)
            new_face.bottom_face = find_face_from_id(
                old_face.bottom_face.face_id)

        return new_grid_faces

    def traversed_order_as_copy(self):
        return {Grid3d.TRAVERSED_ORDER_HORIZON: \
                    [f_id for f_id in self.traversed_order[
                        Grid3d.TRAVERSED_ORDER_HORIZON]],
                Grid3d.TRAVERSED_ORDER_TO_LOWER_RIGHT: \
                    [f_id for f_id in self.traversed_order[
                        Grid3d.TRAVERSED_ORDER_TO_LOWER_RIGHT]],
                Grid3d.TRAVERSED_ORDER_TO_UPPER_RIGHT: \
                    [f_id for f_id in self.traversed_order[
                        Grid3d.TRAVERSED_ORDER_TO_UPPER_RIGHT]]}

    def __str__(self):
        s = super(Grid3d, self).__str__() + "(n_div={}) : \n".format(self.n_div)
        for grid_face in self.grid_faces:
            s += grid_face.__str__() + "\n"
        return s


class GridFace(object):
    def __init__(self, face_id, left_face, right_face, bottom_face,
                 vertices_idx=None):
        self.face_id = face_id

        if vertices_idx is None:
            vertices_idx = OrderedDict()
        self.vertices_idx = vertices_idx

        self.left_face = left_face
        self.right_face = right_face
        self.bottom_face = bottom_face

    def set_vertex_idx(self, idx, alpha, beta):
        self.vertices_idx[(alpha, beta)] = idx

    def get_vertex_idx(self, alpha, beta):
        return self.vertices_idx[(alpha, beta)]

    def top_vertex_idx(self):
        return self.get_vertex_idx(0, 0)

    def left_vertex_idx(self):
        return self.get_vertex_idx(1, 0)

    def right_vertex_idx(self):
        return self.get_vertex_idx(0, 1)

    def get_coordinates(self, vertex_idx):
        return [k for k, v in self.vertices_idx.items() if v == vertex_idx]


    def __str__(self):
        s = "[face ID : {}]\n".format(self.face_id) + \
            "left face : {}\nright face : {}\nbottom face : {}\n".format(
                self.left_face.face_id, self.right_face.face_id,
                self.bottom_face.face_id) + \
            "vertex indices : (alpha, beta) -> [idx]\n"
        for key, idx in self.vertices_idx.items():
            alpha, beta = key
            s += "({0:^3},{1:^3}) -> {2:^2}\n".format(alpha, beta, idx)
        return s
