#!/usr/bin/env python
# coding: utf-8

import unittest
from src.grid import Grid


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.path_grid = '../res/new_regular_ico.grd'
        self.path_save = '../test.obj'
        self.n_div = 4

    def tearDown(self):
        pass

    def test_load(self):
        """

        load()メソッドのテスト
        インスタンスのfile_typeとface_infoをチェック

        """
        grid = Grid.load(self.path_grid, self.n_div)
        self.assertEqual(grid.file_type.name, Grid.FILE_TYPE.GRD.name)
        for face in grid.face_info:
            self.assertIsInstance(face, Grid.FaceInfo)

    def test_divide_face(self):
        """

        divide_face()メソッドのテスト
        グリッド分割後のvertexの数をチェック

        """
        grid = Grid.load(self.path_grid, n_div=1)
        self.assertEqual(len(grid.vertices), 12)

        grid = Grid.load(self.path_grid, n_div=2)
        self.assertEqual(len(grid.vertices), 42)

        grid = Grid.load(self.path_grid, n_div=3)
        self.assertEqual(len(grid.vertices), 92)

        grid = Grid.load(self.path_grid, n_div=4)
        self.assertEqual(len(grid.vertices), 162)

    def test_save(self):
        """

        save()メソッドのテスト

        """
        grid = Grid.load(self.path_grid, self.n_div)
        grid.file_type = Grid.FILE_TYPE.OBJ
        grid.save(self.path_save)


if __name__ == '__main__':
    unittest.main()
