#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np


class _Obj3d(object):
    """

    ３次元空間上のモデル情報を保持するクラス

    """

    def __init__(self, vertices, normal_vertices=None, face_vertices=None):
        """

        :type vertices : list or tuple or np.ndarray
        :param vertices: 全頂点情報

        :type normal_vertices: list or tuple or np.ndarray
        :param normal_vertices: 各法線ベクトルを定義する頂点情報

        :type face_vertices: list or tuple or np.ndarray
        :param face_vertices: 各面を構成する頂点情報

        """

        # assertion
        self.__check_array(vertices, is_nullable=False)
        self.__check_array(normal_vertices, is_nullable=True)
        self.__check_array(face_vertices, is_nullable=True)

        # Immutableなnumpy配列として保持
        self.vertices = _Obj3d.__as_immutable_array(vertices)
        self.normal_vertices = _Obj3d.__as_immutable_array(normal_vertices)
        self.face_vertices = _Obj3d.__as_immutable_array(face_vertices)

    @staticmethod
    def __check_array(list_mem, is_nullable=False):
        """

        メンバ配列がリスト又はNumpy配列であることをチェックする関数

        :type list_mem: list or np.ndarray
        :param list_mem: リスト又はNumpy配列

        :type is_nullable: bool
        :param is_nullable: Noneを許容するかどうか
        """

        if is_nullable and list_mem is None:
            return

        assert list_mem is not None

        # xyzがリスト or Numpy Arrayであるかチェック
        if not isinstance(list_mem, np.ndarray):
            # iterator
            assert hasattr(list_mem, "__getitem__")
            for xyz in list_mem:
                assert hasattr(xyz, "__getitem__")
                assert len(xyz) == 3
                x, y, z = xyz
                assert not hasattr(x, "__getitem__")
                assert not hasattr(y, "__getitem__")
                assert not hasattr(z, "__getitem__")
        else:
            # numpy array
            for xyz in list_mem:
                assert len(xyz) == 3
                x, y, z = xyz
                assert not isinstance(x, np.ndarray)
                assert not isinstance(y, np.ndarray)
                assert not isinstance(z, np.ndarray)

    @staticmethod
    def __as_immutable_array(array):
        if array is None:
            return None

        array = np.asarray(array)
        array.flags.writeable = False

        return array

    def vertices_as_copy(self):
        """

        頂点座標リストのコピーを返す

        """

        if self.vertices is None:
            return None

        return np.array(self.vertices)

    def normals_as_copy(self):
        """

        法線ベクトルを定義する頂点座標リストのコピーを返す

        """

        if self.normal_vertices is None:
            return None

        return np.array(self.normal_vertices)

    def faces_as_copy(self):
        """

        面を定義する頂点座標リストのコピーを返す

        """

        if self.face_vertices is None:
            return None

        return np.array(self.face_vertices)

    def center(self):
        """

        頂点群の重心が座標軸の原点となるように、全ての頂点座標を平行移動

        """

        center_vertices = np.mean(self.vertices, axis=0)
        return _Obj3d(self.vertices - center_vertices,
                      self.normals_as_copy(),
                      self.faces_as_copy())

    def normal(self):
        """

        重心から頂点までの距離が最大1となるように、全ての頂点座標を正規化する

        """

        center_vertices = np.mean(self.vertices, axis=0)

        centered_obj3d = self.center()

        max_norm = np.max(np.linalg.norm(centered_obj3d.vertices, axis=1))

        normalized_vertices = centered_obj3d.vertices / max_norm

        return _Obj3d(normalized_vertices + center_vertices,
                      self.normals_as_copy(),
                      self.faces_as_copy())

    def scale(self, r):
        """

        頂点群の重心から各頂点までの距離をr倍する

        :type r: float
        :param r: 距離倍率

        """

        center_vertices = np.mean(self.vertices, axis=0)

        centered_obj3d = self.center()

        return _Obj3d(centered_obj3d.vertices_as_copy() * r + center_vertices,
                      self.normals_as_copy(),
                      self.faces_as_copy())

    @staticmethod
    def load(path):
        """

        ファイルパスの拡張子を識別してファイル読み込みを行い、Obj3dオブジェクトを返す

        :type path: str
        :param path: ファイルパス

        """
        ext = os.path.splitext(path)[1]

        if ext == ".obj":
            obj3d = _Obj3d.__load_obj(path)
        elif ext == ".off":
            obj3d = _Obj3d.__load_off(path)
        else:
            raise IOError("Obj3d::__init__() : failed to load {}.".format(path))

        return obj3d

    @staticmethod
    def __load_off(off_file):
        """

        .off形式のファイルを読み込み、頂点座標のみを取得

        :type off_file: str
        :param off_file: .offファイル名

        """

        with open(off_file) as f:
            # コメント・空行を除去
            lines = filter(lambda x: x != '\n' and x[0] != "#", f.readlines())

            # 一行目はファイルフォーマット名
            if "OFF" not in lines.pop(0):
                raise IOError("file must be \"off\" format file.")

            # 頂点数、面数、辺数
            n_vertices, n_faces, n_edges = map(int, lines.pop(0).split(' '))

            # 頂点座標を取得
            vertices = np.array([map(float, lines[i].split(' '))
                                 for i in xrange(n_vertices)])

            # 面を構成する頂点のインデックス
            faces = np.array(
                [map(int, lines[n_vertices + i][3:].rstrip().split(' '))
                 for i in xrange(n_faces)])

        return _Obj3d(vertices, None, faces)

    @staticmethod
    def __load_obj(obj_file):
        """

        .objファイルを読み込み、頂点情報のみを取得

        :type obj_file : str
        :param obj_file: ファイルパス

        """

        with open(obj_file) as f:
            lines = filter(lambda x: x != "\n" and x[0] != "#",
                           [line.strip().split() for line in f.readlines()])

            vertices = np.array([list(map(float, line[1:])) for line in lines if
                                 line[0] == 'v'])
            normals = np.array([list(map(float, line[1:])) for line in lines if
                                line[0] == 'vn'])
            faces = np.array(
                [list(map(lambda x: x - 1, map(int, line[1:]))) for line in
                 lines if line[0] == 'f'])

        return _Obj3d(vertices, normals, faces)
