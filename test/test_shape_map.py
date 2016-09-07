#!/usr/bin/env python
# coding: utf-8

import unittest

import numpy as np

from src.grid.icosahedron_grid import IcosahedronFace
from src.shape_map import ShapeMapCreator


class TestShapeMap(unittest.TestCase):
    def setUp(self):
        self.obj3d_path = "../res/stanford_bunny.obj"
        self.grid_path = "../res/new_regular_ico.grd"

        self.shp_file_root = "../res/shape_map"

        self.cls = 0
        self.n_div = 3
        self.is_train = True
        self.scale_grid = 2

    def tearDown(self):
        pass

    def test_tomas_moller(self):
        """

        ShapeMap::tomas_moller()のテスト

        """

        print "\nTest Map2D::tomas_moller() ..."

        map = ShapeMapCreator(obj3d_path=self.obj3d_path,
                              grd_path=self.grid_path,
                              cls=self.cls,
                              n_div=self.n_div,
                              scale_grid=self.scale_grid)

        v0 = np.array([0., 0., 0.])
        v1 = np.array([1., 0., 1.])
        v2 = np.array([0., 1., 1.])
        origin = np.array([0., 0., 1.])

        def assert_penetration(end, solution):
            end = np.asarray(end)
            solution = np.asarray(solution)
            result = map.tomas_moller(origin, end, v0, v1, v2)
            self.assertTrue((np.array(result) == solution).all())

        # penetrate
        assert_penetration([0.5, 0.5, 0], [0.25, 0.25, 0.5])

        # don't penetrate
        assert_penetration([2., 2., 2.], None)

        # vertex check
        assert_penetration([0., 0., 0.], [0., 0., 0.])
        assert_penetration([1., 0., 1.], [1., 0., 1.])
        assert_penetration([0., 1., 1.], [0., 1., 1.])

        # border check
        assert_penetration([1., 1., 1.], [0.5, 0.5, 1.])
        assert_penetration([0., 1., 0.], [0., 0.5, 0.5])
        assert_penetration([1., 0., 0.], [0.5, 0, 0.5])

    def test_save_map_as_dstm(self):
        creator = ShapeMapCreator(obj3d_path=self.obj3d_path,
                                  grd_path=self.grid_path,
                                  cls=self.cls,
                                  n_div=self.n_div,
                                  scale_grid=self.scale_grid)

        horizon_map = creator.create(
            directions=(IcosahedronFace.DIRECTION.HORIZON,))[0]
        horizon_map.save(self.shp_file_root, '0')

        upper_left_map = creator.create(
            directions=(IcosahedronFace.DIRECTION.UPPER_LEFT,))[0]
        upper_left_map.save(self.shp_file_root, '0')

        upper_right_map = creator.create(
            directions=(IcosahedronFace.DIRECTION.UPPER_RIGHT,))[0]
        upper_right_map.save(self.shp_file_root, '0')


if __name__ == '__main__':
    unittest.main()
