#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
from obj3d import Obj3d


class Model(Obj3d):
    """
    3Dモデルの頂点情報のみを保持するクラス
    """

    FILE_TYPE_OFF = "OFF"
    FILE_TYPE_OBJ = "OBJ"

    def __init__(self, vertices, normals, faces, file_type):
        super(Model, self).__init__(vertices, normals, faces, file_type)

    @staticmethod
    def center(model):
        """

        モデルの重心が座標軸の原点となるように、全ての頂点座標を平行移動

        :type model: Model
        :param model: Modelオブジェクト

        """
        if not isinstance(model, Model):
            raise TypeError("Model::center()")

        v_average = np.mean(model.vertices, axis=0)
        model.vertices -= v_average

    @staticmethod
    def normal(model):
        """

        重心から頂点までの距離が最大1となるように、全ての頂点座標を正規化する

        :type model: Model
        :param model: Modelオブジェクト

        """
        if not isinstance(model, Model):
            raise TypeError("Model::normal()")

        v_average = np.mean(model.vertices, axis=0)
        model.vertices -= v_average
        max_norm = np.max(np.linalg.norm(model.vertices, axis=1))
        model.vertices /= max_norm
        model.vertices += v_average

    @staticmethod
    def scale(model, r):
        """

        モデルの重心から頂点までの距離をr倍する

        :type model: Model
        :param model: Modelオブジェクト

        :type r: int
        :param r: 距離倍率

        """
        if not isinstance(model, Model):
            raise TypeError("Model::scale()")

        v_average = np.mean(model.vertices, axis=0)
        model.vertices -= v_average
        model.vertices *= r
        model.vertices += v_average

    @staticmethod
    def load(path):
        """

        ファイルパスの拡張子を識別してファイル読み込みを行い、Modelオブジェクトを返す

        :type path: str
        :param path: ファイルパス

        :rtype: Model
        :return: Modelオブジェクト

        """
        ext = os.path.splitext(path)[1]

        if ext == ".obj":
            model = Model.__load_obj(path)
        elif ext == ".off":
            model = Model.__load_off(path)
        else:
            raise IOError("Map2D::__init__() : failed to load {}.".format(path))

        return model

    @staticmethod
    def __load_off(off_file):
        """

        .off形式のファイルを読み込み、頂点座標のみを取得

        :type off_file: str
        :param off_file: .offファイル名

        :rtype : Model
        :return : Modelオブジェクト

        """

        vertices = None
        faces = None

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

        return Model(vertices, np.array([]), faces, Model.FILE_TYPE_OFF)

    @staticmethod
    def __load_obj(obj_file):
        """

        .objファイルを読み込み、頂点情報のみを取得

        :type obj_file : str
        :param obj_file: ファイルパス

        :rtype : Model
        :return: Modelオブジェクト

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

        return Model(vertices, normals, faces, Model.FILE_TYPE_OBJ)

    def save(self, file_name):
        if self.file_type == Model.FILE_TYPE_OFF:
            self.__save_off(file_name)
        elif self.file_type == Model.FILE_TYPE_OBJ:
            self.__save_obj(file_name)
        else:
            raise NotImplementedError

    def __save_off(self, off_file):
        """

        Modelオブジェクトの内容を.off形式で保存

        :type off_file: str
        :param off_file: .offファイルパス

        """
        name, ext = os.path.splitext(off_file)
        if ext != ".off" or ext == "":
            off_file = name + ".off"

        with open(off_file, "w") as f:
            # OFFファイル先頭行
            f.write("OFF\n")
            # 頂点数 面数 法線数
            f.write(
                "{0} {1} {2}\n\n".format(len(self.vertices), len(self.faces),
                                         len(self.normals)))

            # 頂点情報
            for x, y, z in self.vertices:
                f.write("{0} {1} {2}\n".format(x, y, z))

            # 面情報
            for p1, p2, p3 in self.faces:
                f.write("3  {0} {1} {2}\n".format(p1, p2, p3))

                # 法線情報(NotImplemented)

    def __save_obj(self, obj_file):
        """

        Modelオブジェクトの内容を.obj形式で保存

        :type obj_file: str
        :param obj_file: .objファイルパス

        """
        name, ext = os.path.splitext(obj_file)
        if ext != ".obj" or ext == "":
            obj_file = name + ".obj"

        with open(obj_file, "w") as f:
            # OBJファイル先頭行コメント
            f.write("# OBJ file format with ext .obj\n")
            f.write("# vertex count = {}\n".format(len(self.vertices)))

            if self.faces is not None:
                f.write("# face count = {}\n".format(len(self.faces)))

            # 頂点情報
            for x, y, z in self.vertices:
                f.write("v {0} {1} {2}\n".format(x, y, z))

            # 面情報
            # objファイルの面情報インデックスは１始まりなので、+1する
            if self.faces is not None:
                for p1, p2, p3 in self.faces:
                    f.write("f {0} {1} {2}\n".format(p1 + 1, p2 + 1, p3 + 1))

                    # 法線情報(NotImplemented)


if __name__ == '__main__':
    # parse off
    off_model = Model.load("../res/stanford_bunny.off")
    print ".off vertices : ", off_model.vertices.shape
    print ".off faces : ", off_model.faces.shape
    # parse obj
    obj_model = Model.load("../res/stanford_bunny.obj")
    print ".obj vertices : ", obj_model.vertices.shape
    print ".off normals: ", obj_model.normals.shape
    print ".obj faces : ", obj_model.faces.shape

    print np.mean(off_model.vertices, axis=0)
    Model.center(off_model)
    print np.mean(off_model.vertices, axis=0)

    print np.max(np.linalg.norm(off_model.vertices, axis=1))
    Model.normal(off_model)
    print np.max(np.linalg.norm(off_model.vertices, axis=1))

    obj_model.save("../res/test.obj")
    off_model.save("../res/test.obj")
