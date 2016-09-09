#!/usr/bin/env python
# coding: utf-8

from PyQt4 import QtGui


def critical_message_box(window, title, message):
    QtGui.QMessageBox.critical(window, title, message)
