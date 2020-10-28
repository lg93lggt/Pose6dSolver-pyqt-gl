# -*- coding: utf-8 -*-
# ref: https://www.cnblogs.com/superxuezhazha/p/6195328.html
# ref: https://riptutorial.com/zh-CN/pyqt5/example/29500/%E5%9F%BA%E6%9C%AC%E7%9A%84pyqt%E8%BF%9B%E5%BA%A6%E6%9D%A1
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *
from OpenGL.GL import *

import sys
import time
import struct
import logging
import cv2
import numpy as np

VIDEO_WIDTH = 512
VIDEO_HEIGHT = 424
playerMutex = QMutex() # 创建线程锁

# 底部控制条，开始、暂停、进度条等
class PlayerControl(QDialog):
    videoPlayStarted = pyqtSignal()
    videoPlayPaused = pyqtSignal()
    videoPlayStoped = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_event()
        self.thread_pause = False
        
    def init_ui(self):
        self.setWindowTitle('Progress Bar')
        self.setFixedHeight(80)
        self.progress = QProgressBar(self)
        self.progress.setGeometry(0, 0, 500, 25)
        self.progress.setMaximum(100)
        self.buttonStart = QPushButton('Start', self)
        self.buttonPause = QPushButton('Pause', self)
        self.buttonStop = QPushButton('Stop', self)
        self.buttonStart.move(0, 30)
        self.buttonPause.move(90, 30)
        self.buttonStop.move(180, 30)
        
    def init_event(self):
        self.buttonStart.clicked.connect(self.onButtonStartClick)
        self.buttonPause.clicked.connect(self.onButtonPauseClick)
        self.buttonStop.clicked.connect(self.onButtonStopClick)

    def onButtonStartClick(self):
        if self.thread_pause:
            playerMutex.unlock()
            self.thread_pause = False
        
        self.buttonStart.setEnabled(False)
        self.buttonPause.setEnabled(True)
        self.buttonStop.setEnabled(True)
        self.videoPlayStarted.emit()
        
    def onButtonPauseClick(self):
        playerMutex.lock()
        self.thread_pause = True
        self.buttonStart.setEnabled(True)
        self.buttonPause.setEnabled(False)
        self.buttonStop.setEnabled(True)
        self.videoPlayPaused.emit()
        
    def onButtonStopClick(self):
        self.progress.setValue(0)
        if self.thread_pause:
            playerMutex.unlock()
            self.thread_pause = False
        
        self.buttonStart.setEnabled(True)
        self.buttonPause.setEnabled(False)
        self.buttonStop.setEnabled(False)
        self.videoPlayStoped.emit()
        
    def onProcessChanged(self, value):
        self.progress.setValue(value)

class VideoPlayer(QThread):
    """
    Runs a VideoPlayer thread.
    """
    updateView = pyqtSignal(bytes, int, int)
    progressChanged = pyqtSignal(int)
    
    def __init__(self, video_file):
        super(VideoPlayer, self).__init__()
        self._run = False
        self.video_pause = True
        self.video_Stop = True
        self.video_file = video_file
    
    def get_frame_count(self):
        # 自定义格式，在视频末尾增加了帧总数，8个字节
        with open(self.video_file, "rb") as f:
            f.seek(f.seek(0, 2) - 8, 0)
            frame_count = struct.unpack('Q', f.read(8))[0]
        logging.info("frame_count: %s" %frame_count)
        return frame_count
    
    def onVideoPlayStarted(self):
        self.video_pause = False
        self.video_Stop = False
        self.start()
        
    def onVideoPlayPaused(self):
        self.video_pause = True
        self.video_Stop = False
        
    def onVideoPlayStoped(self):
        self.video_pause = True
        self.video_Stop = True
        self._run = False
        
    def run(self):
        cap = cv2.VideoCapture(self.video_file)
        if not cap:
            return
        frame_index = 0
        total_frame_num = self.get_frame_count()
        self._run = True
        while self._run:
            if self.video_pause:
                playerMutex.lock()
                self.video_pause = False
                playerMutex.unlock()
                continue
            ret, frame = cap.read()
            if not ret:
                continue
            if self.video_Stop:
                break
            if total_frame_num and total_frame_num > 0:
                frame_index += 1
                progress = frame_index*100 / total_frame_num
                self.progressChanged.emit(progress)
            img = cv2.resize(frame, (VIDEO_WIDTH, VIDEO_HEIGHT), interpolation = cv2.INTER_AREA)

            # 用绿色(0, 255, 0)来画出矩形
            x, y, w, h = 10, 10, 200, 300
            img = cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
  
            # Using cv2.putText() method 
            img = cv2.putText(img, 'OpenCV', (50, 50), cv2.FONT_HERSHEY_SIMPLEX , 1, (255, 0, 0), 2, cv2.LINE_AA)

            # Our operations on the frame come here
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_data = rgb.tobytes()
            if self.video_Stop: # 防止此时已经退出
                break
            # Display the resulting frame
            self.updateView.emit(img_data, rgb.shape[0], rgb.shape[1])
        cap.release()
            
    def stop(self):
        self._run = False

# 播放视频的opengl窗口
class VideoView(QGLWidget):
    def __init__(self, parent=None):
        super(VideoView, self).__init__(parent)
        self.width, self.height = VIDEO_WIDTH, VIDEO_HEIGHT
        self.texture, self.data = None, None
        if parent:
            self.resize(parent.size())
        
    def update_view(self, data, height, width):
        self.data = data
        self.height = height
        self.width = width
        self.updateGL()

    def initializeGL(self):
        glClearColor(0.5, 0.5, 0.5, 1.0)

        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)

        glClearDepth(2000.0)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glOrtho(0, self.width, self.height, 0.0, 0.0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


    def paintGL(self):
        if self.data is not None:
            glClearColor(.5, .5, .5, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            # , width = self.data.shape[:2]
            glTexImage2D(GL_TEXTURE_2D,
                         0,
                         3,
                         self.width,
                         self.height,
                         0,
                         GL_RGB,
                         GL_UNSIGNED_BYTE,
                         self.data)
            glLoadIdentity()
    
            glEnable(GL_TEXTURE_2D)
    
            glBegin(GL_TRIANGLE_FAN)
            glColor4f(255.0, 255.0, 255.0, 255.0)
            glTexCoord2f(0, 0); glVertex3f(0, 0, 0)
            glTexCoord2f(1, 0); glVertex3f(self.width, 0, 0)
            glTexCoord2f(1, 1); glVertex3f(self.width, self.height, 0)
            glTexCoord2f(0, 1); glVertex3f(0, self.height, 0)
            glEnd()

# 组合播放窗口和进度条
class CustomVideoPlayer(QDialog):
    def __init__(self, video_file):
        super().__init__()
        self.setFixedSize(900, 600)
        self.videoView = VideoView()
        self.playerControl = PlayerControl()
        self.videoPlayer = VideoPlayer(video_file)
        self.init_event()
        self.init_ui()
        
    def init_event(self):
        self.playerControl.videoPlayStarted.connect(self.videoPlayer.onVideoPlayStarted)
        self.playerControl.videoPlayPaused.connect(self.videoPlayer.onVideoPlayPaused)
        self.playerControl.videoPlayStoped.connect(self.videoPlayer.onVideoPlayStoped)
        self.videoPlayer.progressChanged.connect(self.playerControl.onProcessChanged)
        self.videoPlayer.updateView.connect(self.videoView.update_view)
    
    def init_ui(self):
        self.v_box = QVBoxLayout()
        self.v_box.addWidget(self.videoView)
        self.v_box.addWidget(self.playerControl)
        self.setLayout(self.v_box)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomVideoPlayer('C:/Users/Li/work/veily/_output/8de396d944ffc01adcdf4c10a9cf752a.mp4')
    window.show()
    sys.exit(app.exec_())
