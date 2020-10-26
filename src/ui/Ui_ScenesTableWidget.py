# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/veily/LiGan/Pose6dSolver-pyqt/ui_files/ScenesTableWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(240, 686)
        Form.setMaximumSize(QtCore.QSize(240, 16777215))
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.table_widget = QtWidgets.QTableWidget(Form)
        self.table_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.table_widget.setWordWrap(True)
        self.table_widget.setCornerButtonEnabled(True)
        self.table_widget.setObjectName("table_widget")
        self.table_widget.setColumnCount(0)
        self.table_widget.setRowCount(0)
        self.table_widget.horizontalHeader().setVisible(True)
        self.table_widget.horizontalHeader().setCascadingSectionResizes(False)
        self.table_widget.horizontalHeader().setHighlightSections(False)
        self.table_widget.horizontalHeader().setSortIndicatorShown(False)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.verticalHeader().setCascadingSectionResizes(False)
        self.table_widget.verticalHeader().setSortIndicatorShown(False)
        self.table_widget.verticalHeader().setStretchLastSection(False)
        self.horizontalLayout.addWidget(self.table_widget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.table_widget.setSortingEnabled(False)

