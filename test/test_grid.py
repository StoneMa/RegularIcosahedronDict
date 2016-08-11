#!/usr/bin/env python
# coding: utf-8

import unittest
from src.grid import Grid


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.path_grid = '../res/new_regular_ico.grd'
        self.path_save = '../test.obj'
        self.n_div = 40

    def tearDown(self):
        pass

    def test_load(self):
        grid = Grid.load(self.path_grid)
        print grid

    def test_grid_mem(self):
        grid = Grid.load(self.path_grid)
        for face in grid.face_info:
            self.assertIsInstance(face, Grid.FaceInfo)
        print grid

    def test_divide_face(self):
        grid = Grid.load(self.path_grid)
        grid.divide_face(self.n_div)
        print grid

    def test_save(self):
        grid = Grid.load(self.path_grid)
        grid.divide_face(40)
        grid.file_type = Grid.FILE_TYPE.OBJ
        grid.save(self.path_save)


if __name__ == '__main__':
    unittest.main()
