#!/usr/bin/env python
# coding: utf-8

import unittest
import numpy as np
from src._obj3d import _Obj3d


class _TestObj3d(unittest.TestCase):
    def setUp(self):
        self.vertices = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.normal_vertices = [[0, 1, 2]]
        self.face_vertices = [[0, 1, 2]]

    def tearDown(self):
        pass

    def test_init(self):
        obj3d = _Obj3d(self.vertices, self.normal_vertices, self.face_vertices)

        vertices = np.array(self.vertices)
        normal_vertices = np.array(self.normal_vertices)
        face_vertices = np.array(self.face_vertices)

        obj3d_npy = _Obj3d(vertices, normal_vertices, face_vertices)

    def test_arrays_as_copy(self):
        obj3d = _Obj3d(self.vertices, self.normal_vertices, self.face_vertices)

        self.assertNotEqual(id(self.vertices), id(obj3d.vertices))
        self.assertNotEqual(id(self.normal_vertices), id(obj3d.normal_vertices))
        self.assertNotEqual(id(self.face_vertices), id(obj3d.face_vertices))

        self.assertNotEqual(id(self.vertices), id(obj3d.vertices_as_copy()))
        self.assertNotEqual(id(self.normal_vertices),
                            id(obj3d.normals_as_copy()))
        self.assertNotEqual(id(self.face_vertices),
                            id(obj3d.faces_as_copy()))

    def test_center(self):
        obj3d = _Obj3d(self.vertices, self.normal_vertices, self.face_vertices)

        centered_obj3d = obj3d.center()

        center_vertices = np.mean(centered_obj3d.vertices, axis=0)

        epsilon = np.finfo(float).eps * 10

        cx, cy, cz = center_vertices
        self.assertAlmostEqual(cx, epsilon)
        self.assertAlmostEqual(cy, epsilon)
        self.assertAlmostEqual(cz, epsilon)

    def test_normal(self):
        obj3d = _Obj3d(self.vertices, self.normal_vertices, self.face_vertices)

        center_vertices = np.mean(obj3d.vertices, axis=0)

        normalized_obj3d = obj3d.normal()

        epsilon = np.finfo(float).eps * 10

        self.assertAlmostEqual(
            np.linalg.norm(normalized_obj3d.vertices - center_vertices,
                           axis=1).max(), 1., delta=epsilon)


if __name__ == '__main__':
    unittest.main()
