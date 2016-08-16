#!/usr/bin/env python
# coding: utf-8


import os
import numpy as np
from obj3d import Obj3d


class Grid(Obj3d):
    """
    距離マップ生成用グリッドクラス
    face情報・normal情報は失われる
    代わりに各グリッド面の情報FaceInfoが保持される
    """

    EPSILON = np.finfo(np.float).eps

    INDEX_UNDEFINED = None

    def __init__(self, vertices, face_info):

        super(Grid, self).__init__(vertices, None, None, Obj3d.FILE_TYPE.GRD)

        self.face_info = face_info
        self.n_div = 1

    @staticmethod
    def load(grd_file):

        if os.path.splitext(grd_file)[-1] != ".grd":
            raise IOError(
                "IcoGrid::__init__ : file path is incorrect : {}".format(
                    grd_file))

        vertices = []
        faces = []
        adjacent_faces = []

        face_info = []

        with open(grd_file) as f:

            for line in f.readlines():

                line = line.strip().split()

                if len(line) == 0 or line[0] == '#':
                    continue

                if line[0] == 'v':
                    vertices.append(np.array(map(float, line[1:])))

                if line[0] == 'f':
                    faces.append(np.array(map(int, line[1:])))

                if line[0] == 'af':
                    adjacent_faces.append(np.array(map(int, line[2:])))

            for fid, fv in enumerate(faces):
                face_info.append(
                    Grid.FaceInfo(fid,
                                  Grid.VertexInfo(fv[0], fid, 0, 0),
                                  Grid.VertexInfo(fv[1], fid, 1, 0),
                                  Grid.VertexInfo(fv[2], fid, 0, 1),
                                  None, None, None))

            for f_info in face_info:
                id_left, id_right, id_bottom = adjacent_faces[f_info.face_id]
                f_info.left_face_info = face_info[id_left]
                f_info.right_face_info = face_info[id_right]
                f_info.bottom_face_info = face_info[id_bottom]

        return Grid(vertices, face_info)

    def divide_face(self, n_div):

        assert n_div > 0

        new_vertices = np.empty(shape=(0, 3))

        for f_info in self.face_info:
            top_vertex = self.vertices[f_info.top_vertex_info.vertex_idx]
            left_vertex = self.vertices[f_info.left_vertex_info.vertex_idx]
            right_vertex = self.vertices[f_info.right_vertex_info.vertex_idx]

            left_vector = left_vertex - top_vertex
            right_vector = right_vertex - top_vertex

            new_vertex_info = []

            for sum_length in xrange(n_div + 1):
                for i in xrange(sum_length + 1):
                    alpha = sum_length - i
                    beta = i
                    new_vertex = left_vector * float(alpha) / n_div + \
                                 right_vector * float(beta) / n_div + \
                                 top_vertex

                    # 重複チェック
                    check_duplicate = (
                        np.abs(new_vertex - new_vertices) < Grid.EPSILON).all(
                        axis=1)

                    length_new_vertices = len(new_vertices)

                    if length_new_vertices > 0 and check_duplicate.any():
                        v_idx = int(np.argwhere(check_duplicate))
                    else:
                        v_idx = length_new_vertices
                        new_vertices = np.vstack((new_vertices, new_vertex))

                    new_vertex_info.append(
                        Grid.VertexInfo(v_idx, f_info.face_id, alpha, beta))

            f_info.vertex_info = new_vertex_info

        self.vertices = new_vertices
        self.n_div = n_div

    def traverse(self, center_face_info, direction, n_face_traverse=10):

        if direction == 'upper':
            odd_face_info = 'right_face_info'
            even_face_info = 'bottom_face_info'
            get_init_row_size = lambda step: step
            get_alpha_beta = lambda step, s, is_odd: \
                (s, self.n_div - step) if is_odd else (self.n_div - step, s)
        elif direction == 'lower':
            odd_face_info = 'bottom_face_info'
            even_face_info = 'left_face_info'
            get_init_row_size = lambda step: step
            get_alpha_beta = lambda step, s, is_odd: \
                (self.n_div - step, s) if is_odd else (s, self.n_div - step)
        elif direction == 'horizontal':
            odd_face_info = 'right_face_info'
            even_face_info = 'left_face_info'
            get_init_row_size = lambda step: self.n_div - step
            get_alpha_beta = lambda step, s, is_odd: \
                (step - s, s) if is_odd else (s, step - s)
        else:
            raise NotImplementedError('specified direction is undefined.')

        # 面一周分のリスト
        traversed_face_info = []
        tmp_face_info = center_face_info
        for i in xrange(n_face_traverse):
            traversed_face_info.append(tmp_face_info)
            if i % 2 == 0:
                tmp_face_info = getattr(tmp_face_info, odd_face_info)
            else:
                tmp_face_info = getattr(tmp_face_info, even_face_info)

        vertex_indices = []

        # 各行のインデックスを求める
        for step in xrange(self.n_div + 1):

            row = [Grid.INDEX_UNDEFINED] * get_init_row_size(step)

            tmp_step = step

            for tf_info_idx, tf_info in enumerate(traversed_face_info):
                # 重複を防ぐため、面の行最後の頂点は見ない（次の隣接面の最初に捜査する）
                for ts in xrange(tmp_step):
                    alpha, beta = get_alpha_beta(tmp_step, ts,
                                                 tf_info_idx % 2 == 0)

                    row.append(tf_info.get_vertex_info(alpha, beta))

                # 別の面に移ると面の上下が逆になるので、tmp_stepの値も反転する
                tmp_step = self.n_div - tmp_step

            # 距離マップの後ろにパディングを追加
            row += [Grid.INDEX_UNDEFINED] * (
                self.n_div - get_init_row_size(step))
            # 一行分のインデックスをlistとして格納
            vertex_indices.append(row)

        return np.asarray(vertex_indices)

    def save(self, file_name):
        name, ext = os.path.splitext(file_name)
        if ext != ".off":
            file_name = name + ".off"
        self._save_off(file_name)

    def __str__(self):
        str = super(Grid, self).__str__() + " -> \n"
        for f_info in self.face_info:
            str += f_info.__str__() + "\n"
        return str

    class FaceInfo(object):
        def __init__(self, face_id,
                     top_vertex_info, left_vertex_info, right_vertex_info,
                     left_face_info, right_face_info, bottom_face_info):
            self.face_id = face_id

            self.top_vertex_info = top_vertex_info
            self.left_vertex_info = left_vertex_info
            self.right_vertex_info = right_vertex_info

            self.vertex_info = [top_vertex_info,
                                left_vertex_info,
                                right_vertex_info]

            self.left_face_info = left_face_info
            self.right_face_info = right_face_info
            self.bottom_face_info = bottom_face_info

        def get_vertex_info(self, alpha, beta):
            for v_info in self.vertex_info:
                if v_info.alpha == alpha and v_info.beta == beta:
                    return v_info
            return None

        def __str__(self):
            str = super(Grid.FaceInfo, self).__str__() + "\n" + \
                  "face ID : {:2}".format(self.face_id) + "\n" + \
                  "Left Face ID: {:2} \nRight Face ID : {:2}\nBottom Face ID : {:2}\n".format(
                      self.left_face_info.face_id,
                      self.right_face_info.face_id,
                      self.bottom_face_info.face_id)
            for v_info in self.vertex_info:
                str += v_info.__str__() + "\n"
            return str

    class VertexInfo(object):
        """
        グリッド頂点情報クラス
        """

        def __init__(self, vertex_idx, face_id, alpha, beta):
            self.vertex_idx = vertex_idx
            self.face_id = face_id
            self.alpha = alpha
            self.beta = beta

        def __str__(self):
            return super(Grid.VertexInfo, self).__str__() + \
                   " -> idx : {}, face ID : {} alpha : {}, beta : {}".format(
                       self.vertex_idx, self.face_id, self.alpha, self.beta)
