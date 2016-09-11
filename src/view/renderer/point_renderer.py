#!/usr/bin/env python
# coding: utf-8

from OpenGL import GL

from abstract_renderer import AbstractRenderer
from src.obj.obj3d import Obj3d


class PointRenderer(AbstractRenderer):
    def __init__(self, model):
        """

        :type model: Obj3d
        :param model: 描画する３Dオブジェクト

        """
        self.model = model

    def render(self):
        """

        OpenGLによる描画を行う

        """

        vertices = self.model.vertices if self.model is not None else []

        GL.glBegin(GL.GL_QUADS)
        for vx, vy, vz in vertices:
            GL.glVertex3f(vx, vy, vz)
        GL.glEnd()
