#!/usr/bin/env python
# coding: utf-8

from src.obj.grid.base_grid import BaseGrid
from base_shape_map_factory import BaseShapeMapFactory
from uni_shape_map import UniShapeMap


class UniShapeMapFactory(BaseShapeMapFactory):
    def __init__(self, model_id, obj3d, grid, n_div, cls, grid_scale,
                 uni_scan_directions):
        """

        :type model_id: int or long:
        :param model_id: 対象3DモデルID

        :type obj3d: Obj3d
        :param obj3d: 形状マップ生成対象の３Dオブジェクト

        :type grid: TriangleGrid
        :param grid: 形状マップを生成するための正三角形からなるグリッド

        :type n_div: int or long
        :param n_div: グリッド分割数

        :type cls: int or long
        :param cls: クラスラベル

        :type grid_scale: float
        :param grid_scale: グリッドのスケール率

        :type uni_scan_direction: list(BaseFace.UNI_SCAN_DIRECTION)
        :param uni_scan_direction: 生成するマップの単一面の走査方向リスト
                                   引数にとったパターン分のマップをcreate()で生成する

        """
        super(UniShapeMapFactory, self).__init__(model_id, obj3d, grid, n_div,
                                                 cls, grid_scale)
        self.uni_scan_directions = uni_scan_directions

    def create(self):
        """

        Gridの単一面に対応するShapeMapオブジェクトを生成する

        :rtype: list(UniShapeMap)
        :return: UniShapeMapオブジェクト

        """

        distances = self._distances()

        shape_maps = []
        for direction in self.uni_scan_directions:
            traversed_indices_dict = self.grid.traverse(direction)
            for face_id, vertex_indices_map in traversed_indices_dict.items():
                distance_map = [[distances[idx]
                                 if idx != BaseGrid.VERTEX_IDX_UNDEFINED
                                 else BaseShapeMapFactory.DIST_UNDEFINED
                                 for idx in row]
                                for row in vertex_indices_map]
                shape_maps.append(
                    UniShapeMap(self.map_id, distance_map, self.cls,
                                self.grid.n_div, face_id, direction))
        return shape_maps
