#!/usr/bin/env python
# coding: utf-8

import unittest
import numpy as np
from src._grid import Grid3d


class TestGrid3d(unittest.TestCase):
    def setUp(self):
        self.vertices = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.grid_faces = [[0, 1, 2]]

        self.grid_path = "../res/new_regular_ico.grd"

        self.is_print_enabled = False

    def tearDown(self):
        pass

    def test_init(self):
        # list
        Grid3d(self.vertices, self.grid_faces, n_div=1)
        # numpy
        Grid3d(np.array(self.vertices), np.array(self.grid_faces), n_div=1)

    def test_load(self):
        grid3d = Grid3d.load(self.grid_path)

        if self.is_print_enabled:
            print grid3d


if __name__ == '__main__':
    unittest.main()
