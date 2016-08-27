#!/usr/bin/env python
# coding: utf-8

import unittest
import numpy as np
from src.grid import IcosahedronGrid, IcosahedronFace


class TestGrid3d(unittest.TestCase):
    def setUp(self):
        self.vertices = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.grid_faces = [[0, 1, 2]]

        self.grid_path = "../res/new_regular_ico.grd"

        self.n_div = 2

        self.is_print_enabled = False

    def tearDown(self):
        pass

    def test_init(self):
        # list
        IcosahedronGrid(self.vertices, self.grid_faces, n_div=1, traversed_order=None)
        # numpy
        IcosahedronGrid(np.array(self.vertices), np.array(self.grid_faces), n_div=1,
                        traversed_order=None)

    def test_load(self):
        grid3d = IcosahedronGrid.load(self.grid_path)

        if self.is_print_enabled:
            print grid3d

    def test_divide_face(self):

        # 各頂点の所属する面数をチェックする関数
        def assert_n_vertices(grid, exist_n_vertices):
            for i, v in enumerate(grid.vertices):
                coordinates = []
                for f in grid.grid_faces:
                    coordinates += f.get_coordinates(i)
                n_coordinates = len(coordinates)
                self.assertTrue(n_coordinates in exist_n_vertices)

        grid3d_div1 = IcosahedronGrid.load(self.grid_path).divide_face(1)
        assert_n_vertices(grid3d_div1, [5, ])
        self.assertEqual(len(grid3d_div1.vertices), 12)

        grid3d_div2 = IcosahedronGrid.load(self.grid_path).divide_face(2)
        assert_n_vertices(grid3d_div2, [5, 2])
        self.assertEqual(len(grid3d_div2.vertices), 42)

        grid3d_div3 = IcosahedronGrid.load(self.grid_path).divide_face(3)
        assert_n_vertices(grid3d_div3, [5, 2, 1])
        self.assertEqual(len(grid3d_div3.vertices), 92)

        grid3d_div4 = IcosahedronGrid.load(self.grid_path).divide_face(4)
        assert_n_vertices(grid3d_div4, [5, 2, 1])
        self.assertEqual(len(grid3d_div4.vertices), 162)

    def test_find_face_from_id(self):
        grid3d = IcosahedronGrid.load(self.grid_path)
        for i in xrange(20):
            self.assertEqual(grid3d.find_face_from_id(i).face_id, i)

    def test_traverse(self):
        grid3d = IcosahedronGrid.load(self.grid_path)
        if self.is_print_enabled:
            print grid3d.traverse()


if __name__ == '__main__':
    unittest.main()
