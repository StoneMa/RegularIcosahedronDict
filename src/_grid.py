#!/usr/bin/env python
# coding: utf-8

import numpy as np
from src._obj3d import _Obj3d


class Grid3d(_Obj3d):
    """
    距離マップ生成用グリッドクラス
    face情報・normal情報は失われる
    代わりに各グリッド面の情報GridFaceが保持される
    """

    def __init__(self, vertices, grid_face, n_div):
        """

        :type vertices: list or tuple or np.ndarray
        :param vertices: 全頂点情報

        :type grid_faces: list or tuple
        :param grid_faces: 多角形グリッドの各面の情報

        :type n_div: int
        :param n_div: Grid3dオブジェクトの各面の分割数

        """
        super(Grid3d, self).__init__(vertices)
        self.grid_faces = tuple(grid_face)
        self.n_div = n_div

