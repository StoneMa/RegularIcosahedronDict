#!/usr/bin/env python
# coding: utf-8

import unittest
from src.grid import IcoGrid


class TestIcoGrid(unittest.TestCase):
    PATH_GRID = '../res/new_regular_ico.grd'

    def setUp(self):
        self.grid = IcoGrid(TestIcoGrid.PATH_GRID)

    def tearDown(self):
        pass

    def test_grid_mem(self):
        for face in self.grid.faces:
            self.assertIsInstance(face, IcoGrid.Face)

        print self.grid


if __name__ == '__main__':
    unittest.main()
