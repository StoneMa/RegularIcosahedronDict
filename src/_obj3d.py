#!/usr/bin/env python
# coding: utf-8

import numpy as np


class _Obj3d(object):
    """

    ３次元空間上のモデル情報を保持するクラス

    """

    def __init__(self, vertices, normal_vertices=None, face_vertices=None):

        # assertion
        self.__check_array(vertices, is_nullable=False)
        self.__check_array(normal_vertices, is_nullable=True)
        self.__check_array(face_vertices, is_nullable=True)

        # numpy配列として保持
        self.vertices = np.asarray(vertices)
        self.normal_vertices = np.asarray(normal_vertices)
        self.face_vertices = np.asarray(face_vertices)

        # 各配列はImmutable
        self.vertices.flags.writeable = False
        self.normal_vertices.flags.writeable = False
        self.face_vertices.flags.writeable = False

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

    def vertices_as_copy(self):
        """

        頂点座標リストのコピーを返す

        """

        return np.array(self.vertices)

    def normals_as_copy(self):
        """

        法線ベクトルを定義する頂点座標リストのコピーを返す

        """

        return np.array(self.normal_vertices)

    def faces_as_copy(self):
        """

        面を定義する頂点座標リストのコピーを返す

        """

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
