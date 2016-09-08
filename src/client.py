#!/usr/bin/env python
# coding: utf-8

import os
import time
from src.obj3d import Obj3d
from src.grid.icosahedron_grid import IcosahedronGrid
from src.shape_map import ShapeMapCreator
from src.util.parse_util import parse_cla


def create_shrec_maps(n_div, scale_grid,
                      shrec_off_root="../res/shrec3/off",
                      grd_path="../res/new_regular_ico.grd",
                      cla_file="../res/shrec3/test.cla",
                      shp_file_root="../res/shrec3/shape_map3"):
    cla = parse_cla(cla_file)

    for shrec_name in os.listdir(shrec_off_root):
        start = time.clock()

        print shrec_name, "..."
        shrec_id = int(os.path.splitext(shrec_name[1:])[0])
        shrec_label = [label for label, aff_ids in cla.items()
                       if shrec_id in aff_ids][0]
        shrec_cls = cla.keys().index(shrec_label)

        off_path = os.path.join(shrec_off_root, shrec_name)
        print "creator being generated..."
        creator = ShapeMapCreator(Obj3d.load(off_path),
                                  IcosahedronGrid.load(grd_path),
                                  shrec_cls,
                                  n_div,
                                  scale_grid)

        print "maps being created..."
        horizon, upper_right, upper_left = creator.create_all_direction()
        print horizon
        # horizon.save(shp_file_root, str(shrec_id))
        # upper_right.save(shp_file_root, str(shrec_id))
        # upper_left.save(shp_file_root, str(shrec_id))

        print (time.clock() - start), "s"



if __name__ == '__main__':
    create_shrec_maps(n_div=3, scale_grid=2)
