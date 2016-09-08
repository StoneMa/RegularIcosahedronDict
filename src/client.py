#!/usr/bin/env python
# coding: utf-8

import os
import time
from src.obj3d import Obj3d
from src.grid.icosahedron_grid import IcosahedronGrid
from src.shape_map import ShapeMapCreator
from collections import OrderedDict


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


def parse_cla(cla_file):
    """

    .claファイルを読み込み、所属クラスデータを返す

    :type cla_file: str
    :param cla_file: PATH含むファイル名

    :rtype collections.OrderedDict
    :return: クラスラベル:属するデータの辞書

    """

    # クラス階層情報を保持するツリー
    tree = ClaTree('0')

    # クラスラベルと属するデータIDのマップ
    classifier = OrderedDict()

    with open(cla_file) as f:
        if "PSB" not in f.readline():
            raise IOError("file must be \"cla\" format file.")

        n_class, n_data = map(int, f.readline().split(' '))

        while True:
            line = f.readline()

            if line == '':
                break

            split_line = line.split(' ')

            if len(split_line) == 3:
                # ツリーへクラスを登録
                name, parent_name, n = split_line
                tree.add(name, parent_name)

                # 葉ノードの場合、データIDリストを取得
                if int(n) > 0:
                    ids = [int(f.readline()) for i in xrange(int(n))]
                    classifier.setdefault(name, ids)

    return classifier


class ClaTree(object):
    """
    .claファイル中のクラス階層を表現するクラス
    """

    def __init__(self, root_name):
        self.root = self.ClaNode(root_name, None, 0)

    def __str__(self):
        return self.root.__str__()

    def add(self, name, parent_name):
        self.root.add(name, parent_name, 1)

    def parent(self, name, degree):
        node = self.root.search(name)
        return node.get_parent(degree)

    class ClaNode(object):
        def __init__(self, name, parent, degree, last_node=False):
            self.name = name
            self.parent = parent
            self.children = []
            self.degree = degree
            self.last_node = last_node

        def __str__(self):
            string = self.name
            if self.last_node:
                edge = '\n' + '|   ' * (self.degree - 1) + '    ∟---'
            else:
                edge = '\n' + ('|   ' * self.degree) + '∟---'
            for c in self.children:
                string += edge + c.__str__()
            return string

        def add(self, name, parent_name, degree):
            if parent_name == self.name:
                if len(self.children) > 0:
                    self.children[-1].last_node = False
                node = self.__class__(name, self, degree, True)
                self.children.append(node)
            else:
                for c in self.children:
                    c.add(name, parent_name, degree + 1)

        def search(self, name):
            if self.name == name:
                return self

            for c in self.children:
                node = c.search(name)
                if node is not None:
                    return node
            return None

        def leaf(self):
            if len(self.children) == 0:
                return [self]
            else:
                leaves = []
                for c in self.children:
                    leaves.extend(c.leaf())
                return leaves

        def get_parent(self, degree):
            if self.parent is None:
                return self
            elif self.degree <= degree:
                return self
            else:
                return self.parent.get_parent(degree)


if __name__ == '__main__':
    create_shrec_maps(n_div=3, scale_grid=2)
