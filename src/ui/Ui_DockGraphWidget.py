# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/veily/桌面/LiGan/Pose6dSolver-pyqt-gl/ui_files/DockGraphWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1114, 897)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.dockWidget = QtWidgets.QDockWidget(Form)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.openGLWidget = QtWidgets.QOpenGLWidget(self.dockWidgetContents)
        self.openGLWidget.setObjectName("openGLWidget")
        self.gridLayout.addWidget(self.openGLWidget, 0, 0, 1, 1)
        self.dockWidget.setWidget(self.dockWidgetContents)
        self.horizontalLayout_2.addWidget(self.dockWidget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

