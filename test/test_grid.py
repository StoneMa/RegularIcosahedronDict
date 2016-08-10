#!/usr/bin/env python
# coding: utf-8

import unittest
from src.grid import Grid


class TestGrid(unittest.TestCase):
    PATH_GRID = '../res/new_regular_ico.grd'
    PATH_SAVE = '../test.obj'
    N_DIVISION = 40

    def setUp(self):
        self.grid = Grid(TestGrid.PATH_GRID)

    def tearDown(self):
        pass

    def test_grid_mem(self):
        for face in self.grid.faces:
            self.assertIsInstance(face, Grid.GridFace)
        print self.grid

    def test_divide_face(self):
        self.grid.divide_face(TestGrid.N_DIVISION)
        print self.grid

    def test_save_obj(self):
        self.grid.save_obj(TestGrid.PATH_SAVE)
        pass


if __name__ == '__main__':
    unittest.main()
