#!/usr/bin/env python
# coding: utf-8

import os
import sys
import re
import threading
import time

from src.map.factory.band_shape_map_factory import BandShapeMapFactory
from src.map.factory.uni_shape_map_factory import UniShapeMapFactory
from src.obj.grid.base_grid import BaseFace
from src.obj.grid.triangle_grid import TriangleGrid
from src.obj.grid.icosahedron_grid import IcosahedronGrid
from src.obj.obj3d import Obj3d
from src.util.parse_util import parse_cla
from src.view.qt_main import main, MainWindow


def handler(kwargs):
    """

    実行ハンドラ

    """
    n_div = kwargs[MainWindow.KEY_N_DIV]
    grid_scale = kwargs[MainWindow.KEY_GRID_SCALE]
    model_root_path = kwargs[MainWindow.KEY_MODEL_PATH]
    grid_path = kwargs[MainWindow.KEY_GRID_PATH]
    cla_path = kwargs[MainWindow.KEY_CLA_PATH]
    save_root_path = kwargs[MainWindow.KEY_SAVE_PATH]

    def execute():

        cla = parse_cla(cla_path)

        for model_name in os.listdir(model_root_path):

            start = time.clock()

            print model_name, "..."
            model_id = int(re.search('\d+', model_name).group())
            model_label = [label for label, aff_ids in cla.items()
                           if model_id in aff_ids][0]
            cls = cla.keys().index(model_label)

            off_path = os.path.join(model_root_path, model_name)

            print "creator being generated..."
            obj3d = Obj3d.load(off_path)
            grid3d = IcosahedronGrid.load(grid_path)
            factory = UniShapeMapFactory(model_id, obj3d, grid3d, n_div, cls,
                                         grid_scale,
                                         BaseFace.UNI_SCAN_DIRECTION)

            for shape_map in factory.create():
                print shape_map
                shp_path = os.path.join(save_root_path, str(model_id),
                                        shape_map.traverse_direction.name,
                                        "{}.shp".format(shape_map.face_id))
                shape_map.save(shp_path)

            print (time.clock() - start), "s"

    threading.Thread(target=execute).start()


def band_map_handler(kwargs):
    """

    実行ハンドラ

    """
    n_div = kwargs[MainWindow.KEY_N_DIV]
    grid_scale = kwargs[MainWindow.KEY_GRID_SCALE]
    model_root_path = kwargs[MainWindow.KEY_MODEL_PATH]
    grid_path = kwargs[MainWindow.KEY_GRID_PATH]
    cla_path = kwargs[MainWindow.KEY_CLA_PATH]
    save_root_path = kwargs[MainWindow.KEY_SAVE_PATH]

    def execute():

        cla = parse_cla(cla_path)

        for model_name in os.listdir(model_root_path):

            start = time.clock()

            print model_name, "..."
            model_id = int(re.search('\d+', model_name).group())
            model_label = [label for label, aff_ids in cla.items()
                           if model_id in aff_ids][0]
            cls = cla.keys().index(model_label)

            off_path = os.path.join(model_root_path, model_name)

            print "creator being generated..."
            obj3d = Obj3d.load(off_path)
            grid3d = IcosahedronGrid.load(grid_path)
            factory = BandShapeMapFactory(model_id, obj3d, grid3d, n_div, cls,
                                          grid_scale, TriangleGrid.BAND_TYPE, 0)

            for shape_map in factory.create():
                print shape_map
                shp_path = os.path.join(save_root_path, str(model_id),
                                        "{}.shp".format(
                                            shape_map.band_type.name))
                shape_map.save(shp_path)

            print (time.clock() - start), "s"

    threading.Thread(target=execute).start()


if __name__ == '__main__':
    title, x, y, width, height = sys.argv[1:]
    main(title, int(x), int(y), int(width), int(height), band_map_handler)
