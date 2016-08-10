#!/usr/bin/env python
# coding: utf-8

import unittest
import numpy as np

from src.obj3d import Obj3d


class TestObj3d(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_load(self):
        """

        load()メソッドのテスト
        各メンバの型チェックのみ

        """
        obj3d_off = Obj3d.load("../res/stanford_bunny.off")
        self.assertIsInstance(obj3d_off.vertices, np.ndarray)
        self.assertIsInstance(obj3d_off.normals, np.ndarray)
        self.assertIsInstance(obj3d_off.faces, np.ndarray)
        self.assertEqual(obj3d_off.file_type.name, Obj3d.FILE_TYPE.OFF.name)

        obj3d_obj = Obj3d.load("../res/stanford_bunny.obj")
        self.assertIsInstance(obj3d_obj.vertices, np.ndarray)
        self.assertIsInstance(obj3d_obj.normals, np.ndarray)
        self.assertIsInstance(obj3d_obj.faces, np.ndarray)
        self.assertEqual(obj3d_obj.file_type.name, Obj3d.FILE_TYPE.OBJ.name)

    def test_center(self):
        """

        center()メソッドのテスト
        verticesの座標平均値が誤差epsilon以内かチェック

        """
        epsilon = np.finfo(float).eps * 10

        obj3d_off = Obj3d.load("../res/stanford_bunny.off")
        obj3d_off.center()

        cx, cy, cz = np.mean(obj3d_off.vertices, axis=0)
        self.assertAlmostEqual(cx, epsilon)
        self.assertAlmostEqual(cy, epsilon)
        self.assertAlmostEqual(cz, epsilon)

    def test_normal(self):
        """

        normal()メソッドのテスト
        頂点ベクトルのノルム最大値が1であることをチェック

        """
        obj3d_off = Obj3d.load("../res/stanford_bunny.off")
        obj3d_off.normal()

        center = np.mean(obj3d_off.vertices, axis=0)
        self.assertEqual(
            np.abs(np.linalg.norm(obj3d_off.vertices - center, axis=1)).max(),
            1.)

    def test_scale(self):
        """

        scale()メソッドのテスト
        scale()呼出し後の頂点群が指定倍数拡張されているかチェック

        """
        epsilon = np.finfo(float).eps * 10

        obj3d_off = Obj3d.load("../res/stanford_bunny.off")

        center = np.mean(obj3d_off.vertices, axis=0)

        before_vertices = np.array(obj3d_off.vertices) - center
        obj3d_off.scale(r=2)
        after_vertices = np.array(obj3d_off.vertices) - center

        self.assertTrue(
            (after_vertices - epsilon < before_vertices * 2).all() and
            (before_vertices * 2 < after_vertices + epsilon).all())

    def test_save(self):
        """

        save()メソッドのテスト
        読み込み＋ファイルタイプのチェック

        """
        obj3d_off = Obj3d.load("../res/stanford_bunny.off")
        obj3d_obj = Obj3d.load("../res/stanford_bunny.obj")

        obj3d_off.save("../res/test_save_bunny.off")
        obj3d_obj.save("../res/test_save_bunny.obj")

        obj3d_saved_off = Obj3d.load("../res/test_save_bunny.off")
        obj3d_saved_obj = Obj3d.load("../res/test_save_bunny.obj")

        self.assertEqual(obj3d_saved_off.file_type.name,
                         Obj3d.FILE_TYPE.OFF.name)

        self.assertEqual(obj3d_saved_obj.file_type.name,
                         Obj3d.FILE_TYPE.OBJ.name)


if __name__ == '__main__':
    unittest.main()
