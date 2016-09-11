#!/usr/bin/env python
# coding: utf-8

import StringIO
import sys
import time
import threading
from PyQt4 import QtGui, QtCore
from src.util.app_util import save_cache, load_cache
from qt_gl import GLWidget
from renderer.point_renderer import PointRenderer


class MainWindow(QtGui.QMainWindow):
    """

    プロジェクトをグラフィカルに操作するUIウィンドウ

    """

    LABEL_TEXT_MODEL_PATH = "Model File (.off or .obj) Path"
    LABEL_TEXT_GRID_PATH = "Grid Path"
    LABEL_TEXT_CLA_PATH = ".cla File Path"
    LABEL_TEXT_SAVE_PATH = "Save Path"
    LABEL_TEXT_N_DIV_PATH = "N-Division"
    LABEL_TEXT_GRID_SCALE_PATH = "Grid Scale"

    LABEL_TEXT_GROUP = "Settings"

    BUTTON_TEXT_FILE_DIALOG = "..."
    BUTTON_TEXT_CREATE = "create"

    DIALOG_TITLE_FILE = "open file"
    DIALOG_TITLE_FOLDER = "choice folder"

    FILE_DIALOG_INIT_PATH = "../res"
    CACHE_PATH = "../.cache"

    KEY_MODEL_PATH = "model_path"
    KEY_GRID_PATH = "grid_path"
    KEY_CLA_PATH = "cla_path"
    KEY_SAVE_PATH = "save_path"
    KEY_N_DIV = "n_div"
    KEY_GRID_SCALE = "grid_scale"

    class SygnalHost(QtCore.QObject):
        """

        単一シグナルを持つオブジェクト

        """
        sygnal = QtCore.pyqtSignal()

    def __init__(self, title, x, y, width, height):
        """

        :type title: str
        :param title: ウィンドウタイトル

        :type x: int
        :param x: ウィンドウのx座標

        :type y: int
        :param y: ウィンドウのy座標

        :type width: int
        :param width: ウィンドウの幅

        :type height: int
        :param height: ウィンドウの高さ

        """
        super(MainWindow, self).__init__()

        self.setGeometry(x, y, width, height)
        self.setWindowTitle(title)

        self.parent_widget = QtGui.QWidget()

        ### result layout ###

        self.te_result = QtGui.QTextEdit(self)
        vl_result = QtGui.QVBoxLayout()
        vl_result.addWidget(self.gl_widget)
        vl_result.addWidget(self.te_result)

        ### path input layout ###

        # text box
        self.tb_model_path = self.get_cached_line_edit(MainWindow.CACHE_PATH,
                                                       MainWindow.KEY_MODEL_PATH)
        self.tb_grid_path = self.get_cached_line_edit(MainWindow.CACHE_PATH,
                                                      MainWindow.KEY_GRID_PATH)
        self.tb_cla_path = self.get_cached_line_edit(MainWindow.CACHE_PATH,
                                                     MainWindow.KEY_CLA_PATH)
        self.tb_save_path = self.get_cached_line_edit(MainWindow.CACHE_PATH,
                                                      MainWindow.KEY_SAVE_PATH)
        self.tb_n_div = self.get_cached_line_edit(MainWindow.CACHE_PATH,
                                                  MainWindow.KEY_N_DIV)
        self.tb_grid_scale = self.get_cached_line_edit(MainWindow.CACHE_PATH,
                                                       MainWindow.KEY_GRID_SCALE)

        # button
        btn_fd_model_path = self.get_file_dialog_button(self.tb_model_path,
                                                        MainWindow.KEY_MODEL_PATH,
                                                        False)
        btn_fd_grid_path = self.get_file_dialog_button(self.tb_grid_path,
                                                       MainWindow.KEY_GRID_PATH,
                                                       True)
        btn_fd_cla_path = self.get_file_dialog_button(self.tb_cla_path,
                                                      MainWindow.KEY_CLA_PATH,
                                                      True)
        btn_fd_save_path = self.get_file_dialog_button(self.tb_save_path,
                                                       MainWindow.KEY_SAVE_PATH,
                                                       False)

        # path layout row
        hl_model_path = self.get_file_path_layout(self.tb_model_path,
                                                  btn_fd_model_path)
        hl_grid_path = self.get_file_path_layout(self.tb_grid_path,
                                                 btn_fd_grid_path)
        hl_cla_path = self.get_file_path_layout(self.tb_cla_path,
                                                btn_fd_cla_path)
        hl_save_path = self.get_file_path_layout(self.tb_save_path,
                                                 btn_fd_save_path)

        # path layout
        vl_path = QtGui.QVBoxLayout()
        vl_path.addWidget(QtGui.QLabel(MainWindow.LABEL_TEXT_MODEL_PATH))
        vl_path.addLayout(hl_model_path)
        vl_path.addWidget(QtGui.QLabel(MainWindow.LABEL_TEXT_GRID_PATH))
        vl_path.addLayout(hl_grid_path)
        vl_path.addWidget(QtGui.QLabel(MainWindow.LABEL_TEXT_CLA_PATH))
        vl_path.addLayout(hl_cla_path)
        vl_path.addWidget(QtGui.QLabel(MainWindow.LABEL_TEXT_SAVE_PATH))
        vl_path.addLayout(hl_save_path)
        vl_path.addWidget(QtGui.QLabel(MainWindow.LABEL_TEXT_N_DIV_PATH))
        vl_path.addWidget(self.tb_n_div)
        vl_path.addWidget(QtGui.QLabel(MainWindow.LABEL_TEXT_GRID_SCALE_PATH))
        vl_path.addWidget(self.tb_grid_scale)

        gw_path = QtGui.QGroupBox(MainWindow.LABEL_TEXT_GROUP)
        gw_path.setLayout(vl_path)

        vl_path_group = QtGui.QVBoxLayout()
        vl_path_group.addWidget(gw_path)

        ### create button layout ###

        self.btn_create = QtGui.QPushButton(self)
        self.btn_create.setText(MainWindow.BUTTON_TEXT_CREATE)
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

        # start std-output to tb_result.
        self.__show_stdout_as_result()

    def get_cached_line_edit(self, cache_path, cache_key):
        """

        QLineEditを返す
        QLineEditには前回最後に入力した内容が入る

        :type cache_path: str
        :param cache_path: キャッシュ保存パス

        :type cache_key: str
        :param cache_key: キャッシュされたデータのキー

        :type: QtGui.QLineEdit
        :return: キャッシュされたパスを読み込んだQLineEditオブジェクト

        """
        line_edit = QtGui.QLineEdit(self)
        cache = load_cache(cache_path, cache_key)
        if cache is not None:
            line_edit.setText(cache)
        return line_edit

    def get_file_dialog_button(self, line_edit, cache_key, is_file):
        """

        ファイルダイアログを開くQPushButtonを返す
        ファイルダイアログで読み込まれたパスはキャッシュされる

        :type line_edit: QtGui.QLineEdit
        :param line_edit: パスを入力するQLineEditオブジェクト

        :type cache_key: str
        :param cache_key: キャッシュされたデータのキー

        :type is_file: bool
        :param is_file: ファイルパス読み込みかどうか（Falseの場合ディレクトリパス読み込み）

        :rtype: QtGui.QPushButton
        :return: ファイルダイアログを開くQPushButton

        """

        button = QtGui.QPushButton(self)
        button.setText(MainWindow.BUTTON_TEXT_FILE_DIALOG)

        def handler():
            if is_file:
                f_dialog = QtGui.QFileDialog.getOpenFileName
                title = MainWindow.DIALOG_TITLE_FILE
            else:
                f_dialog = QtGui.QFileDialog.getOpenFileName
                title = MainWindow.DIALOG_TITLE_FOLDER
            path = f_dialog(self, title, MainWindow.FILE_DIALOG_INIT_PATH)
            line_edit.setText(path)
            save_cache(MainWindow.CACHE_PATH, cache_key, path)

        self.connect(button, QtCore.SIGNAL('clicked()'), handler)
        return button

    def get_file_path_layout(self, line_edit, button):
        """

        ファイルパスを入力するQLineEditと
        ファイルダイアログを開くQPushButtonを統合したレイアウトを返す

        :type line_edit: QtGui.QLineEdit
        :param line_edit: QLineEditオブジェクト

        :type button: QtGui.QPushButton
        :param button: QPushButtonオブジェクト

        """
        hl_model_path = QtGui.QHBoxLayout()
        hl_model_path.addWidget(line_edit)
        hl_model_path.addWidget(button)
        return hl_model_path

    def set_on_create_button_click_handler(self, on_create_button_clicked):
        """

        createボタンが押された時の処理を記述した関数を
        createボタンに設定する

        :type on_create_button_clicked: func
        :param on_create_button_clicked: createボタンに設定するハンドラ


        """

        self.connect(self.btn_create, QtCore.SIGNAL('clicked()'),
                     on_create_button_clicked)

    def __show_stdout(self):

        """

        標準出力を文字列として逐次取得し、GUI上に表示する

        """

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


def main(init, title, x, y, width, height):
    """

    GUI Main関数

    :type init: func(QtGui.QMainWindow)
    :param init: 初期化関数

    :type title: str
    :param title: ウィンドウタイトル

    :type x: int
    :param x: ウィンドウのx座標

    :type y: int
    :param y: ウィンドウのy座標

    :type width: int
    :param width: ウィンドウの幅

    :type height: int
    :param height: ウィンドウの高さ

    """
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(title, x, y, width, height)
    init(window)
    sys.exit(app.exec_())
