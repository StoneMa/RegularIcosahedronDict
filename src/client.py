#!/usr/bin/env python
# coding: utf-8

import os
import time
import threading
from src.view.qt_util import critical_message_box
from src.view.qt_main import main, MainWindow
from src.obj3d import Obj3d
from src.grid.icosahedron_grid import IcosahedronGrid
from src.shape_map import ShapeMapCreator
from src.util.parse_util import parse_cla


def init(window):
    """

    client初期化処理

    :type window: MainWindow
    :param window: Qtメインウィンドウ

    """

    def on_create_button_click():

        model_path = str(window.tb_model_path.text())
        grid_path = str(window.tb_grid_path.text())
        cla_path = str(window.tb_cla_path.text())
        save_path = str(window.tb_save_path.text())

        try:
            n_div = int(str(window.tb_n_div.text()))
            grid_scale = float(str(window.tb_grid_scale.text()))
        except TypeError, e:
            if "n_div" in e.message:
                critical_message_box(window, "",
                                     "N-Division should be a number.")
            else:
                critical_message_box(window, "",
                                     "Grid Scale should be a number.")
        else:
            create_shrec_maps(n_div, grid_scale, model_path, grid_path,
                              cla_path, save_path)

    window.set_on_create_button_click_listener(on_create_button_click)


def create_shrec_maps(n_div, scale_grid, shrec_off_root, grd_path, cla_file,
                      shp_file_root):

    def execute():
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
            obj3d = Obj3d.load(off_path)
            grid3d = IcosahedronGrid.load(grd_path)
            creator = ShapeMapCreator(obj3d,
                                      grid3d,
                                      shrec_cls,
                                      n_div,
                                      scale_grid)

            print "maps being created..."
            horizon, upper_right, upper_left = creator.create_all_direction()
            print horizon
            horizon.save(shp_file_root, str(shrec_id))
            upper_right.save(shp_file_root, str(shrec_id))
            upper_left.save(shp_file_root, str(shrec_id))

            print (time.clock() - start), "s"

    threading.Thread(target=execute).start()


if __name__ == '__main__':
    main(init)
