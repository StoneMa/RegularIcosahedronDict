#!/usr/bin/env python
# coding: utf-8

import unittest
import numpy as np
from src._obj3d import _Obj3d


class _TestObj3d(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        vertices = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        normal_vertices = [[0, 1, 2]]
        face_vertices = [[0, 1, 2]]

        obj3d = _Obj3d(vertices, normal_vertices, face_vertices)

        vertices = np.array(vertices)
        normal_vertices = np.array(normal_vertices)
        face_vertices = np.array(face_vertices)

        obj3d_npy = _Obj3d(vertices, normal_vertices, face_vertices)


if __name__ == '__main__':
    unittest.main()
