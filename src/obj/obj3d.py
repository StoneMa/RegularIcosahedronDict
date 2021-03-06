#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np


class Obj3d(object):
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
        self.vertices = Obj3d.__as_immutable_array(vertices)
        self.normal_vertices = Obj3d.__as_immutable_array(normal_vertices)
        self.face_vertices = Obj3d.__as_immutable_array(face_vertices)

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
        """

        引数の配列からImmutableなnumpy配列を生成して返す

        :type array: list or tuple or np.ndarray
        :param array: 入力配列

        :rtype: np.ndarray
        :return: Immutableなnumpy配列

        """
        if array is None:
            return None

        array = np.asarray(array)
        array.flags.writeable = False

        return array

    def vertices_as_copy(self):
        """

        頂点座標リストのコピーを返す

        :rtype: np.ndarray
        :return: 頂点座標リストのコピー

        """

        if self.vertices is None:
            return None

        return np.array(self.vertices)

    def normals_as_copy(self):
        """

        法線ベクトルを定義する頂点座標リストのコピーを返す

        :rtype: np.ndarray
        :return: 法線ベクトルを定義する頂点座標リストのコピー

        """

        if self.normal_vertices is None:
            return None

        return np.array(self.normal_vertices)

    def faces_as_copy(self):
        """

        面を定義する頂点座標リストのコピーを返す

        :rtype: np.ndarray
        :return: 面を定義する頂点座標リストのコピー

        """

        if self.face_vertices is None:
            return None

        return np.array(self.face_vertices)

    def center(self):
        """

        頂点群の重心が座標軸の原点となるように、全ての頂点座標を平行移動

        :rtype: Obj3d
        :return: 座標を平行移動したObj3dオブジェクトのコピー

        """

        center_vertices = np.mean(self.vertices, axis=0)
        return Obj3d(self.vertices - center_vertices,
                     self.normals_as_copy(),
                     self.faces_as_copy())

    def normal(self):
        """

        重心から頂点までの距離が最大1となるように、全ての頂点座標を正規化する

        :rtype: Obj3d
        :return: 座標を正規化したObj3dオブジェクトのコピー

        """

        center_vertices = np.mean(self.vertices, axis=0)

        centered_obj3d = self.center()

        max_norm = np.max(np.linalg.norm(centered_obj3d.vertices, axis=1))

        normalized_vertices = centered_obj3d.vertices / max_norm

        return Obj3d(normalized_vertices + center_vertices,
                     self.normals_as_copy(),
                     self.faces_as_copy())

    def scale(self, r):
        """

        頂点群の重心から各頂点までの距離をr倍する

        :type r: float
        :param r: 距離倍率

        :rtype: Obj3d
        :return: 座標を拡大縮小したObj3dオブジェクトのコピー

        """

        center_vertices = np.mean(self.vertices, axis=0)

        centered_obj3d = self.center()

        return Obj3d(centered_obj3d.vertices_as_copy() * r + center_vertices,
                     self.normals_as_copy(),
                     self.faces_as_copy())

    def rotate(self, theta, axis_vector):
        """

        頂点群をaxis_vectorを軸として角度thetaだけ回転する

        :type theta: float
        :param theta: 回転角

        :type axis_vector: np.ndarray
        :param axis_vector: 軸ベクトル

        :rtype: Obj3d
        :return: 回転後のObj3dオブジェクトのコピー
        """

        assert isinstance(theta, float)
        assert len(axis_vector) == 3
        for elem in axis_vector:
            assert isinstance(elem, (int, long, float))

        # 軸成分
        ax, ay, az = axis_vector / np.linalg.norm(axis_vector)

        cos = np.cos(theta)
        sin = np.sin(theta)

        # 回転行列
        r_mtr = np.array([[ax * ax * (1. - cos) + cos,
                           ax * ay * (1. - cos) - az * sin,
                           az * ax * (1. - cos) + ay * sin],
                          [ax * ay * (1. - cos) + az * sin,
                           ay * ay * (1. - cos) + cos,
                           ay * az * (1. - cos) - ax * sin],
                          [az * ax * (1. - cos) - ay * sin,
                           ay * az * (1. - cos) + ax * sin,
                           az * az * (1. - cos) + cos]])

        center = np.mean(self.vertices, axis=0)

        centered_vertices = self.vertices - center

        return Obj3d(np.dot(centered_vertices, r_mtr.T) + center,
                     self.normals_as_copy(), self.faces_as_copy())

    @staticmethod
    def load(file_path):
        """

        ファイルパスの拡張子を識別してファイル読み込みを行い、Obj3dオブジェクトを返す

        :type file_path: str
        :param file_path: ファイルパス

        :rtype: Obj3d
        :return: ファイル読み込みによって生成されたObj3dオブジェクト

        """
        ext = os.path.splitext(file_path)[1]

        if ext == ".obj":
            obj3d = Obj3d.__load_obj(file_path)
        elif ext == ".off":
            obj3d = Obj3d.__load_off(file_path)
        else:
            raise IOError(
                "Obj3d::__init__() : failed to load {}.".format(file_path))

        return obj3d

    @staticmethod
    def __load_off(off_file_path):
        """

        .off形式のファイルを読み込み、頂点座標のみを取得

        :type off_file_path: str
        :param off_file_path: .offファイル名

        :rtype: Obj3d
        :return: .offファイル読み込みによって生成されたObj3dオブジェクト

        """

        with open(off_file_path) as f:
            # コメント・空行を除去
            lines = filter(lambda x: x != '\n' and x[0] != "#",
                           f.readlines())

            # 一行目はファイルフォーマット名
            if "OFF" not in lines.pop(0):
                raise IOError("file must be \"off\" format file.")

            # 頂点数、面数、辺数
            n_vertices, n_faces, n_edges = map(int, lines.pop(0).split(' '))

            # 頂点座標を取得
            vertices = np.array([map(float, lines[i].strip().split(' '))
                                 for i in xrange(n_vertices)])

            # 面を構成する頂点のインデックス
            faces = np.array(
                [map(int, lines[n_vertices + i].strip().split(' '))[1:]
                 for i in xrange(n_faces)])

            return Obj3d(vertices, None, faces)

    @staticmethod
    def __load_obj(obj_file_path):
        """

        .objファイルを読み込み、頂点情報のみを取得

        :type obj_file_path : str
        :param obj_file_path: ファイルパス

        :rtype: Obj3d
        :return: .objファイル読み込みによって生成されたObj3dオブジェクト

        """

        with open(obj_file_path) as f:
            lines = filter(lambda x: x != "\n" and x[0] != "#",
                           [line.strip().split() for line in f.readlines()])

            vertices = np.array(
                [list(map(float, line[1:])) for line in lines if
                 line[0] == 'v'])
            normals = np.array(
                [list(map(float, line[1:])) for line in lines if
                 line[0] == 'vn'])
            faces = np.array(
                [list(map(lambda x: x - 1, map(int, line[1:]))) for line in
                 lines if line[0] == 'f'])

        return Obj3d(vertices, normals, faces)

    def save(self, file_path):
        """

        Obj3dオブジェクトの内容を指定した拡張子の形式で保存

        :type file_path: str
        :param file_path: 保存するファイルパス

        """
        ext = os.path.splitext(file_path)[1]

        if ext == ".obj":
            self._save_obj(file_path)
        elif ext == ".off":
            self._save_off(file_path)
        else:
            raise NotImplementedError

    def _save_off(self, off_file_path):
        """

        Obj3dオブジェクトの内容を.off形式で保存

        :type off_file_path: str
        :param off_file_path: .offファイルパス

        """
        name, ext = os.path.splitext(off_file_path)
        if ext != ".off" or ext == "":
            off_file_path = name + ".off"

        with open(off_file_path, "w") as f:
            # OFFファイル先頭行
            f.write("OFF\n")
            # 頂点数 面数 法線数
            len_vertices = len(self.vertices)
            len_fv = 0 if self.face_vertices is None else len(
                self.face_vertices)
            len_nv = 0 if self.normal_vertices is None else len(
                self.face_vertices)
            f.write("{0} {1} {2}\n\n".format(len_vertices, len_fv, len_nv))

            # 頂点情報
            for x, y, z in self.vertices:
                f.write("{0} {1} {2}\n".format(x, y, z))

            # 面情報
            if self.face_vertices is not None:
                for p1, p2, p3 in self.face_vertices:
                    f.write("3  {0} {1} {2}\n".format(p1, p2, p3))

                    # 法線情報(NotImplemented)

    def _save_obj(self, obj_file_path):
        """

        Modelオブジェクトの内容を.obj形式で保存

        :type obj_file_path: str
        :param obj_file_path: .objファイルパス

        """
        name, ext = os.path.splitext(obj_file_path)
        if ext != ".obj" or ext == "":
            obj_file_path = name + ".obj"

        with open(obj_file_path, "w") as f:
            # OBJファイル先頭行コメント
            f.write("# OBJ file format with ext .obj\n")
            f.write("# vertex count = {}\n".format(len(self.vertices)))

            if self.face_vertices is not None:
                f.write("# face count = {}\n".format(len(self.face_vertices)))

            # 頂点情報
            for x, y, z in self.vertices:
                f.write("v {0} {1} {2}\n".format(x, y, z))

            # 面情報
            # objファイルの面情報インデックスは１始まりなので、+1する
            if self.face_vertices is not None:
                for p1, p2, p3 in self.face_vertices:
                    f.write("f {0} {1} {2}\n".format(p1 + 1, p2 + 1, p3 + 1))

                    # 法線情報(NotImplemented)
