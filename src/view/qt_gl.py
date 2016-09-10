#!/usr/bin/env python
# coding: utf-8

from PyQt4 import QtCore, QtGui, QtOpenGL
from OpenGL import GL
from src.util.qt_util import Color


class GLWidget(QtOpenGL.QGLWidget):
    """
    OpenGLを用いた3D描画を行うQtウィジェットクラス
    """

    class GLLight(object):
        def __init__(self, type, position, diffuse):
            self.type = type
            self.position = position
            self.diffuse = diffuse
            # self.specular = specular

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self.type.name == other.type.name
            elif isinstance(other, str):
                return self.type.name == other
            else:
                return id(self) == id(other)

    LIGHTS = (
        GLLight(GL.GL_LIGHT0, (-3.0, 0.0, 0.0, 1.0), (1.0, 0.0, 0.0, 1.0)),
        GLLight(GL.GL_LIGHT1, (3.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0)),
        GLLight(GL.GL_LIGHT2, (0.0, -3.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0)),
        GLLight(GL.GL_LIGHT3, (0.0, 3.0, 0.0, 1.0), (1.0, 1.0, 1.0, 1.0)))

    DEFAULT_BG_COLOR = Color.DARKULA_DARK

    DEFAULT_CAMERA_LOCATION = (0, 0, -10.0)

    MIN_SIZE = (100, 100)
    DEFAULT_SIZE = (400, 400)

    ROTATE_UNIT = 16.

    SIGNAL_X_ROTATION_CHANGED = QtCore.pyqtSignal(int)
    SIGNAL_Y_ROTATION_CHANGED = QtCore.pyqtSignal(int)
    SIGNAL_Z_ROTATION_CHANGED = QtCore.pyqtSignal(int)

    def __init__(self, renderer, parent=None, bg_color=DEFAULT_BG_COLOR):
        super(GLWidget, self).__init__(parent)

        self.object = 0
        self.rx = 0
        self.ry = 0
        self.rz = 0

        self.last_mouse_pos = QtCore.QPoint()

        self.renderer = renderer

        self.bg_color = bg_color

    def minimumSizeHint(self):
        """
        Widgetの最小サイズ
        :return: QSize
        """
        return QtCore.QSize(*self.MIN_SIZE)

    def sizeHint(self):
        """
        Widgetの推奨サイズ
        :return: QSize
        """
        return QtCore.QSize(*self.DEFAULT_SIZE)

    def set_x_rotation(self, angle):
        """
        x軸の回転を設定
        :param angle: 回転度数
        :return:
        """
        angle %= 360 * self.ROTATE_UNIT
        if angle != self.rx:
            self.rx = angle
            self.SIGNAL_X_ROTATION_CHANGED.emit(angle)
            self.updateGL()

    def set_y_rotation(self, angle):
        """
        y軸の回転を設定
        :param angle: 回転度数
        :return:
        """
        angle %= 360 * self.ROTATE_UNIT
        if angle != self.ry:
            self.ry = angle
            self.SIGNAL_Y_ROTATION_CHANGED.emit(angle)
            self.updateGL()

    def set_z_rotation(self, angle):
        """
        z軸の回転を設定
        :param angle: 回転度数
        :return:
        """
        angle %= 360 * self.ROTATE_UNIT
        if angle != self.rz:
            self.rz = angle
            self.SIGNAL_Z_ROTATION_CHANGED.emit(angle)
            self.updateGL()

    def initializeGL(self):
        """
        OpenGL周辺の設定を初期化
        :return:
        """
        self.qglClearColor(QtGui.QColor.fromRgb(*self.bg_color))
        # 描画オブジェクトの初期化
        self.update_object()
        # シェーディングの設定
        GL.glShadeModel(GL.GL_FLAT)
        # デプスバッファの更新を有効化
        GL.glEnable(GL.GL_DEPTH_TEST)
        # 平面の表のみを描画
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_FRONT)
        # アンチエイリアス
        GL.glEnable(GL.GL_POLYGON_SMOOTH)
        # 陰影付けを有効にする
        GL.glEnable(GL.GL_LIGHTING)
        # 光源のDiffuse/Specular設定
        for l in self.LIGHTS:
            GL.glLightfv(l.type, GL.GL_DIFFUSE, l.diffuse)

    def set_light_enable(self, name, is_enabled):
        """
        光源の有効・無効を切り替え
        :param name: 光源識別用の名前
        :param is_enabled: 有効にするかどうか
        """

        gl_light = self.LIGHTS[self.LIGHTS.index(name)]
        if is_enabled:
            GL.glEnable(gl_light.type)
        else:
            GL.glDisable(gl_light.type)
        self.updateGL()

    def paintGL(self):
        """
        OpenGLによる描画処理
        """
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        # 光源位置設定
        for l in self.LIGHTS:
            GL.glLightfv(l.type, GL.GL_POSITION, l.position)
        # カメラをデフォルト位置からどれだけ移動するか
        GL.glTranslated(*self.DEFAULT_CAMERA_LOCATION)
        GL.glRotated(self.rx / self.ROTATE_UNIT, 1.0, 0.0, 0.0)
        GL.glRotated(self.ry / self.ROTATE_UNIT, 0.0, 1.0, 0.0)
        GL.glRotated(self.rz / self.ROTATE_UNIT, 0.0, 0.0, 1.0)
        GL.glCallList(self.object)

    def resizeGL(self, width, height):
        """
        ウィジェットがリサイズされるときの処理
        :param width: 親ウィジェットの幅
        :param height: 親ウィジェットの高さ
        """
        side = min(width, height)
        if side < 0:
            return

        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def mousePressEvent(self, event):
        """
        マウスが押下された時のイベントリスナー
        :param event: イベントオブジェクト
        """
        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        """
        マウスが移動した時のイベントリスナー
        :param event:  イベントオブジェクト
        """

        if not event.buttons():
            return

        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()

        if QtCore.Qt.LeftButton:
            self.set_x_rotation(self.rx + self.ROTATE_UNIT / 2 * dy)
            self.set_y_rotation(self.ry + self.ROTATE_UNIT / 2 * dx)
        elif QtCore.Qt.RightButton:
            self.set_x_rotation(self.rx + self.ROTATE_UNIT / 2 * dy)
            self.set_z_rotation(self.rz + self.ROTATE_UNIT / 2 * dx)

        self.last_mouse_pos = event.pos()

    def __make_object(self):
        """
        GLWidget上オブジェクトを描画する
        :return:
        """
        genList = GL.glGenLists(1)
        GL.glNewList(genList, GL.GL_COMPILE)

        if self.renderer is not None:
            self.renderer.render()

        GL.glEndList()

        return genList

    def update_object(self):
        """
        描画オブジェクトを更新する
        :return:
        """
        self.object = self.__make_object()
