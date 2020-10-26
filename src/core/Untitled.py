#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2018 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


import sys
import math

from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor, QOpenGLVersionProfile
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
        QWidget)


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.glWidget = GLWidget()

        self.xSlider = self.createSlider()
        self.ySlider = self.createSlider()
        self.zSlider = self.createSlider()

        self.xSlider.valueChanged.connect(self.glWidget.setXRotation)
        self.glWidget.xRotationChanged.connect(self.xSlider.setValue)
        self.ySlider.valueChanged.connect(self.glWidget.setYRotation)
        self.glWidget.yRotationChanged.connect(self.ySlider.setValue)
        self.zSlider.valueChanged.connect(self.glWidget.setZRotation)
        self.glWidget.zRotationChanged.connect(self.zSlider.setValue)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        mainLayout.addWidget(self.xSlider)
        mainLayout.addWidget(self.ySlider)
        mainLayout.addWidget(self.zSlider)
        self.setLayout(mainLayout)

        self.xSlider.setValue(15 * 16)
        self.ySlider.setValue(345 * 16)
        self.zSlider.setValue(0 * 16)

        self.setWindowTitle("Hello GL")

    def createSlider(self):
        slider = QSlider(Qt.Vertical)

        slider.setRange(-180 * 16, 179 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)

        return slider


class GLWidget(QOpenGLWidget):
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.lastPos = QPoint()

        self.trolltechGreen = QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.trolltechPurple = QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(640, 480)

    def setXRotation(self, angle):
        print ("x1", angle)
        angle = self.normalizeAngle(angle)
        print ("x2",angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def initializeGL(self):
        version_profile = QOpenGLVersionProfile()
        version_profile.setVersion(2, 0)
        self.gl = self.context().versionFunctions(version_profile)
        self.gl.initializeOpenGLFunctions()

        self.setClearColor(self.trolltechPurple.darker())
        self.object = self.makeObject()
        self.axises = self.makeAxises()
        self.gl.glShadeModel(self.gl.GL_FLAT)
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        self.gl.glEnable(self.gl.GL_CULL_FACE)

    def paintGL(self):
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        self.gl.glLoadIdentity()
        self.gl.glTranslated(0.0, 0.0, -10.0)
        self.gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        self.gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        self.gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        self.gl.glCallList(self.object)
        self.gl.glLoadIdentity()
        self.gl.glTranslated(0.0, 0.0, -10.0)
        self.gl.glCallList(self.axises)


    def resizeGL(self, width, height):
        print ("resize")
        side = min(width, height)
        if side < 0:
            return

        self.gl.glViewport((width - side) // 2, (height - side) // 2, side,
                side)

        self.gl.glMatrixMode(self.gl.GL_PROJECTION)
        self.gl.glLoadIdentity()
        #self.gl.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        #self.gl.glMatrixMode(self.gl.GL_MODELVIEW)

        sys.path.append("..")
        from Camera import  Camera
        cam = Camera()
        import  json
        with open("/home/veily/桌面/LiGan/Pose6dSolver-pyqt-gl/姿态测量/results_calib/cam_1/camera_pars.json") as f:
            data = json.load(f)
            cam.set_camera_pars(data)
        cam.set_image_shape(480, 640)
        M = cam.to_modelview_gl()
        P = cam.to_projection_gl()

        self.gl.glMatrixMode(self.gl.GL_PROJECTION)
        self.gl.glLoadIdentity()
        self.gl.glLoadMatrixf(P.tolist())
        self.gl.glViewport(0, 0, cam.shape_image.width*2, cam.shape_image.height)
    
        # self.gl.glMatrixMode(self.gl.GL_MODELVIEW)
        # self.gl.glLoadIdentity()
     
        #self.gl.glMultMatrixf(M.tolist())
    




    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)

        self.lastPos = event.pos()

    def makeAxises(self):       
        axisesList = self.gl.glGenLists(1)
        self.gl.glNewList(axisesList, self.gl.GL_COMPILE)
 
        self.gl.glBegin(self.gl.GL_LINES)
        self.gl.glColor4f(1., 0., 0., 1)
        self.gl.glVertex3f(100000 / 1000, 0, 0)
        self.gl.glVertex3f(0, 0, 0)

        self.gl.glColor4f(0., 1., 0., 1)
        self.gl.glVertex3f(0, 100000 / 1000, 0)
        self.gl.glVertex3f(0, 0, 0)

        self.gl.glColor4f(0., 0., 1., 1)
        self.gl.glVertex3f(0, 0, 100000 / 1000)
        self.gl.glVertex3f(0, 0, 0)
        self.gl.glEnd()
        self.gl.glEndList()
        return axisesList


    def makeObject(self):
        genList = self.gl.glGenLists(1)
        self.gl.glNewList(genList, self.gl.GL_COMPILE)

        import sys
        sys.path.append("..")
        from core import FileIO
        model = FileIO.load_model_from_stl_binary("/home/veily/桌面/LiGan/Pose6dSolver-pyqt-gl/测试/models_solve/3D_model.STL")

        self.gl.glColor4f(0., 1., 0., 0.1)
        self.gl.glBegin(self.gl.GL_POLYGON)
        for triangle in model:
                #self.gl.glNormal3f(triangle.normal.x, triangle.normal.y, triangle.normal.z)
            self.gl.glVertex3f(triangle[0][0] / 1000, triangle[0][1] / 1000, triangle[0][2] / 1000)
            self.gl.glVertex3f(triangle[1][0] / 1000, triangle[1][1] / 1000, triangle[1][2] / 1000)
            self.gl.glVertex3f(triangle[2][0] / 1000, triangle[2][1] / 1000, triangle[2][2] / 1000)
        self.gl.glEnd()
        self.gl.glEndList()
        return genList


    def normalizeAngle(self, angle):
        while angle < -180 * 16:
            angle += 360 * 16
        while angle > 180 * 16:
            angle -= 360 * 16
        return angle

    def setClearColor(self, c):
        self.gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        self.gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def draw_background(self, imname):
        """使用四边形绘制背景图像"""
        
        #载入背景图像，转为OpenGL纹理
        bg_image = pygame.image.load(imname).convert()
        bg_data = pygame.image.tostring(bg_image, "RGBX", 1)
        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)
        self.gl.glLoadIdentity()

        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        #绑定纹理
        self.gl.glEnable(self.gl.GL_TEXTURE_2D)
        self.gl.glBindTexture(self.gl.GL_TEXTURE_2D, self.gl.glGenTextures(1))
        self.gl.glTexImage2D(self.gl.GL_TEXTURE_2D, 0, self.gl.GL_RGBA, 640, 480, 0, self.gl.GL_RGBA, self.gl.GL_UNSIGNED_BYTE, bg_data)
        self.gl.glTexParameterf(self.gl.GL_TEXTURE_2D, self.gl.GL_TEXTURE_MAG_FILTER, self.gl.GL_NEAREST)
        self.gl.glTexParameterf(self.gl.GL_TEXTURE_2D, self.gl.GL_TEXTURE_MIN_FILTER, self.gl.GL_NEAREST)
        #创建四方形填充整个窗口
        self.gl.glBegin(self.gl.GL_QUADS)
        self.gl.glTexCoord2f(0.0, 0.0);
        self.gl.glVertex3f(-1.0, -1.0, -1.0)
        self.gl.glTexCoord2f(1.0, 0.0);
        self.gl.glVertex3f(1.0, -1.0, -1.0)
        self.gl.glTexCoord2f(1.0, 1.0);
        self.gl.glVertex3f(1.0, 1.0, -1.0)
        self.gl.glTexCoord2f(0.0, 1.0);
        self.gl.glVertex3f(-1.0, 1.0, -1.0)
        self.gl.glEnd()
        #清除纹理
        self.gl.glDeleteTextures(1)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
