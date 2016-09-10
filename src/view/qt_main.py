#!/usr/bin/env python
# coding: utf-8

import StringIO
import sys
import time
import threading
from PyQt4 import QtGui, QtCore
from src.util.app_util import save_cache, load_cache


class MainWindow(QtGui.QMainWindow):
    class SygnalHost(QtCore.QObject):
        sygnal = QtCore.pyqtSignal()

    def __init__(self, title, x, y, width, height):
        super(MainWindow, self).__init__()

        self.setGeometry(x, y, width, height)
        self.setWindowTitle(title)

        self.parent_widget = QtGui.QWidget()

        # result layout #

        self.te_result = QtGui.QTextEdit(self)

        vl_result = QtGui.QVBoxLayout()
        vl_result.addWidget(self.te_result)

        # path input layout #

        self.tb_model_path = self.get_cached_line_edit("../.cache",
                                                       "model_path")
        self.tb_grid_path = self.get_cached_line_edit("../.cache", "grid_path")
        self.tb_cla_path = self.get_cached_line_edit("../.cache", "cla_path")
        self.tb_save_path = self.get_cached_line_edit("../.cache", "save_path")
        self.tb_n_div = self.get_cached_line_edit("../cache", "n_div")
        self.tb_grid_scale = self.get_cached_line_edit("../cache", "grid_scale")

        btn_fd_model_path = QtGui.QPushButton(self)
        btn_fd_grid_path = QtGui.QPushButton(self)
        btn_fd_cla_path = QtGui.QPushButton(self)
        btn_fd_save_path = QtGui.QPushButton(self)

        def open_file(parent, tb, key):
            def handler():
                path = QtGui.QFileDialog.getOpenFileName(
                    parent, 'open file', '../res')
                tb.setText(path)
                save_cache("../.cache", key, path)

            return handler

        def open_folder(parent, tb, key):
            def handler():
                path = QtGui.QFileDialog.getExistingDirectory(
                    parent, 'open folder', '../res')
                tb.setText(path)
                save_cache("../.cache", key, path)

            return handler

        self.connect(btn_fd_model_path,
                     QtCore.SIGNAL('clicked()'),
                     open_folder(self, self.tb_model_path, "model_path"))

        self.connect(btn_fd_grid_path,
                     QtCore.SIGNAL('clicked()'),
                     open_file(self, self.tb_grid_path, "grid_path"))

        self.connect(btn_fd_cla_path,
                     QtCore.SIGNAL('clicked()'),
                     open_file(self, self.tb_cla_path, "cla_path"))

        self.connect(btn_fd_save_path,
                     QtCore.SIGNAL('clicked()'),
                     open_folder(self, self.tb_save_path, "save_path"))

        hl_model_path = QtGui.QHBoxLayout()
        hl_model_path.addWidget(self.tb_model_path)
        hl_model_path.addWidget(btn_fd_model_path)

        hl_grid_path = QtGui.QHBoxLayout()
        hl_grid_path.addWidget(self.tb_grid_path)
        hl_grid_path.addWidget(btn_fd_grid_path)

        hl_cla_path = QtGui.QHBoxLayout()
        hl_cla_path.addWidget(self.tb_cla_path)
        hl_cla_path.addWidget(btn_fd_cla_path)

        hl_save_path = QtGui.QHBoxLayout()
        hl_save_path.addWidget(self.tb_save_path)
        hl_save_path.addWidget(btn_fd_save_path)

        vl_path = QtGui.QVBoxLayout()
        vl_path.addWidget(QtGui.QLabel("Model Path"))
        vl_path.addLayout(hl_model_path)
        vl_path.addWidget(QtGui.QLabel("Grid Path"))
        vl_path.addLayout(hl_grid_path)
        vl_path.addWidget(QtGui.QLabel(".cla File Path"))
        vl_path.addLayout(hl_cla_path)
        vl_path.addWidget(QtGui.QLabel("Sava Path"))
        vl_path.addLayout(hl_save_path)
        vl_path.addWidget(QtGui.QLabel("N-Division"))
        vl_path.addWidget(self.tb_n_div)
        vl_path.addWidget(QtGui.QLabel("Grid Scale"))
        vl_path.addWidget(self.tb_grid_scale)

        gw_path = QtGui.QGroupBox("Settings")
        gw_path.setLayout(vl_path)

        vl_path_group = QtGui.QVBoxLayout()
        vl_path_group.addWidget(gw_path)

        # create button layout #

        self.btn_create = QtGui.QPushButton(self)
        self.btn_create.setText("create")

        vl_button = QtGui.QVBoxLayout()
        vl_button.addWidget(self.btn_create)

        # combine path input layout and create button layout.
        vl_path_button = QtGui.QVBoxLayout()
        vl_path_button.addLayout(vl_path_group)
        vl_path_button.addLayout(vl_button)

        # inflate
        parent_layout = QtGui.QHBoxLayout()
        parent_layout.addLayout(vl_result)
        parent_layout.addLayout(vl_path_button)

        # set layout
        self.parent_widget.setLayout(parent_layout)
        self.setCentralWidget(self.parent_widget)

        self.show()

        #
        self.__show_stdout_as_result()

    def get_cached_line_edit(self, cache_path, cache_key):
        line_edit = QtGui.QLineEdit(self)
        cache = load_cache(cache_path, cache_key)
        if cache is not None:
            line_edit.setText(cache)
        return line_edit

    def set_on_create_button_click_listener(self, on_create_button_clicked):
        self.connect(self.btn_create, QtCore.SIGNAL('clicked()'),
                     on_create_button_clicked)

    def __show_stdout(self):
        stdout_as_string_io = sys.stdout
        stderr_as_string_io = sys.stderr

        stdout_as_string_io.seek(0)
        stderr_as_string_io.seek(0)
        text_out = stdout_as_string_io.read()
        text_err = stderr_as_string_io.read()

        self.te_result.setText(
            self.te_result.toPlainText() + text_out + text_err)
        cursor = self.te_result.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.te_result.setTextCursor(cursor)

        stdout_as_string_io.close()
        stderr_as_string_io.close()

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        sys.stdout.write(text_out)
        sys.stderr.write(text_err)

        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()

    def __show_stdout_as_result(self, duration=1):
        """

        標準出力を文字列として逐次取得する

        """

        # pyqt signal to show standard output on te_result.
        signal_stdout = MainWindow.SygnalHost()

        # connect
        signal_stdout.sygnal.connect(self.__show_stdout)

        def emit_signal():
            # change sys.stdout to StringIO.
            sys.stdout = StringIO.StringIO()
            sys.stderr = StringIO.StringIO()
            while True:
                signal_stdout.sygnal.emit()
                time.sleep(duration)

        threading.Thread(target=emit_signal).start()


def main(init):
    app = QtGui.QApplication(sys.argv)
    window = MainWindow("a", 0, 0, 800, 450)
    init(window)
    sys.exit(app.exec_())
