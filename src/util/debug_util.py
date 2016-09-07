#!/usr/bin/env python
# coding: utf-8


def assert_type_in_container(container, class_or_type_or_tuple):
    """

    引数に渡したコンテナの各要素に対して型チェックを行う

    :type container: list
    :param container: 要素を型チェックされるコンテナ

    :type class_or_type_or_tuple: T or tuple(T)
    :param class_or_type_or_tuple: 型あるいは型のtuple


    """
    assert hasattr(container, "__getitem__")
    for elem in container:
        assert isinstance(elem, class_or_type_or_tuple)
