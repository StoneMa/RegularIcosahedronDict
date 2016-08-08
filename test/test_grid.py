#!/usr/bin/env python
# coding: utf-8

import unittest
from src.grid import Grid


class TestGrid(unittest.TestCase):
    PATH_GRID = '../res/new_regular_ico.grd'

    def setUp(self):
        self.grid = Grid(TestGrid.PATH_GRID)

    def tearDown(self):
        pass

    def test_grid_mem(self):
        for face in self.grid.faces:
            self.assertIsInstance(face, Grid.GridFace)

        print self.grid


if __name__ == '__main__':
    unittest.main()
