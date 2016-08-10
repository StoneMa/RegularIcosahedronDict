#!/usr/bin/env python
# coding: utf-8

import numpy as np
from obj3d import Obj3d


class Model(Obj3d):
    """
    3Dモデルの頂点情報のみを保持するクラス
    """

    def __init__(self, vertices, normals, faces, file_type):
        super(Model, self).__init__(vertices, normals, faces, file_type)

    @staticmethod
    def load(path):
        obj3d = Obj3d.load(path)
        return Model(obj3d.vertices, obj3d.normals, obj3d.faces,
                     obj3d.file_type)


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
