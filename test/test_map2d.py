#!/usr/bin/env python
# coding: utf-8

import numpy as np
from src.map2d import Map2D


def test_tomas_moller(model_path="../res/stanford_bunny.obj",
                      grid_path="../res/regular_icosahedron.obj",
                      n_div_recursion=0, scale_grid=2):
    map = Map2D(model_path=model_path, grid_path=grid_path,
                n_div_recursion=n_div_recursion, scale_grid=scale_grid)

    v0 = np.array([0., 0., 0.])
    v1 = np.array([1., 0., 1.])
    v2 = np.array([0., 1., 1.])
    origin = np.array([0., 0., 1.])

    def test_penetration(end):
        print map.tomas_moller(origin, end, v0, v1, v2)

    # penetrate
    test_penetration(np.array([0.5, 0.5, 0]))  # [0.25  0.25  0.5 ]

    # don't penetrate
    test_penetration(np.array([2., 2., 2.]))  # None

    # vertex check
    test_penetration(np.array([0., 0., 0.]))  # [0.  0.  0.]
    test_penetration(np.array([1., 0., 1.]))  # [1.  0.  1.]
    test_penetration(np.array([0., 1., 1.]))  # [0.  1.  1.]

    # border check
    test_penetration(np.array([1., 1., 1.]))  # [0.5  0.5  1. ]
    test_penetration(np.array([0., 1., 0.]))  # [0.   0.5  0.5]
    test_penetration(np.array([1., 0., 0.]))  # [0.5  0.   0.5]


if __name__ == '__main__':
    test_tomas_moller()
