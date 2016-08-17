#!/usr/bin/env python
# coding: utf-8

import unittest
import numpy as np
from src._grid import Grid3d


class TestGrid3d(unittest.TestCase):
    def setUp(self):
        self.vertices = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.grid_faces = [[0, 1, 2]]

    def tearDown(self):
        pass

    def test_init(self):
        # list
        Grid3d(self.vertices, self.grid_faces, n_div=1)
        # numpy
        Grid3d(np.array(self.vertices), np.array(self.grid_faces), n_div=1)


if __name__ == '__main__':
    unittest.main()
