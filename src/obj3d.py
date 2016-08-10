#!/usr/bin/env python
# coding: utf-8

class Obj3d(object):
    """
    3次元オブジェクトを表現するクラス
    """

    def __init__(self, vertices, normals, faces, file_type):
        self.vertices = vertices
        self.normals = normals
        self.faces = faces
        self.file_type = file_type
        