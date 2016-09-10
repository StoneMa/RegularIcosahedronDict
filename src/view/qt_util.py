#!/usr/bin/env python
# coding: utf-8

from PyQt4 import QtGui


def critical_message_box(window, title, message):
    """

    警告メッセージボックスを表示する

    :type window: QtGui.QMainWindow
    :param window:
    :param title:
    :param message:
    :return:
    """
    QtGui.QMessageBox.critical(window, title, message)
