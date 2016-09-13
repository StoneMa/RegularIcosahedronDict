#!/usr/bin/env python
# coding: utf-8

from src.obj.grid.base_grid import BaseGrid
from base_shape_map_factory import BaseShapeMapFactory
from band_shape_map import BandShapeMap
from src.util.debug_util import assert_type_in_container


class BandShapeMapFactory(BaseShapeMapFactory):
    def __init__(self, model_id, obj3d, grid, n_div, cls, grid_scale,
                 band_types, center_face_id):
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

        :type band_types: list(BaseGrid.BAND_TYPE)
        :param band_types: 帯形状マップタイプのリスト
                           リスト上の全てのタイプの形状マップをcreate()で生成する

        :type center_face_id: int or long
        :param center_face_id: 帯の中心となる面のID

        """
        super(BandShapeMapFactory, self).__init__(model_id, obj3d, grid, n_div,
                                                  cls, grid_scale)
        assert_type_in_container(band_types, BaseGrid.BAND_TYPE)
        assert isinstance(center_face_id, (int, long))
        self.band_types = band_types
        self.center_face_id = center_face_id

    def create(self):
        """

        Gridを帯状に走査し、BandShapeMapオブジェクトをband_types分生成する

        :rtype: list(BandShapeMap)
        :return: BandShapeMapオブジェクトのリスト

        """

        distances = self._distances()

        shape_maps = []
        for band_type in self.band_types:
            band_vertex_indices_map = self.grid.traverse_band(band_type,
                                                              self.center_face_id)
            distance_map = [[distances[idx]
                             if idx != BaseGrid.VERTEX_IDX_UNDEFINED
                             else BaseShapeMapFactory.DIST_UNDEFINED
                             for idx in row]
                            for row in band_vertex_indices_map]
            shape_maps.append(
                BandShapeMap(self.model_id, distance_map, self.cls,
                             self.grid.n_div, band_type))
        return shape_maps
