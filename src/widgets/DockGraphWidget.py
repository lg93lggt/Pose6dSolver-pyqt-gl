
import sys
from typing import *

import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


sys.path.append("..")
from ui import *
from core import Visualizer, FileIO, geometry
from widgets import TableWidget


class DockGraphWidget(QWidget, Ui_DockGraphWidget.Ui_Form):
    # sig_sub_tabel_double_clicked  = pyqtSignal(str, str, int ,int)
    # sig_choose_points2d_successed = pyqtSignal(str, str, dict, np.ndarray, np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        return

    def _init(self):
        return

    def _update(self):
        return
    

if  __name__ == "__main__": 
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = DockGraphWidget(None)
    widget.show()
    sys.exit(app.exec_())
