import cv2
import numpy as np
import face_recognition
import os 
from datetime import datetime as datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime

import sys
import os
from qtwidgets import Toggle, AnimatedToggle
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

import numpy as np
import math
import pylsl
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from typing import List
import time

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        path = r'C:\\Users\\ASUS\\Desktop\\atten\\image'
        images = []    
        class_name = []    
        my_list = os.listdir(path)
        print("Total Classes Detected:",len(my_list))
            
        for x,image_name in enumerate(my_list):
            current_img = cv2.imread(f'{path}/{image_name}')
            images.append(current_img)
            class_name.append(os.path.splitext(image_name)[0])

        print(f'Student in classes are {class_name}')

        def find_encodings(images):
            encode_list = []
            for img in images:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img)[0]
                encode_list.append(encode)
            return encode_list

        encode_list_registered_faces = find_encodings(images)
        print(encode_list_registered_faces)
        print('Encodings Complete!')
        # capture from web cam
        cap = cv2.VideoCapture(0)
        while True:
            ret, img = cap.read()
            img_from_webcam = cv2.resize(img, (0, 0), None, fx = 0.25, fy = 0.25)
            # img_from_webcam = cv2.resize(img, (300, 300))

            img_from_webcam = cv2.cvtColor(img_from_webcam, cv2.COLOR_BGR2RGB)

            faces_current_frame = face_recognition.face_locations(img_from_webcam)
            encodes_current_frame = face_recognition.face_encodings(img_from_webcam, faces_current_frame) # in case many faces, send face location

            for encode_face, face_location in zip(encodes_current_frame, faces_current_frame):
                matches = face_recognition.compare_faces(encode_list_registered_faces, encode_face)
                face_distance = face_recognition.face_distance(encode_list_registered_faces, encode_face)
                match_faces = np.argmin(face_distance)

                if matches[match_faces]:
                    student_name = class_name[match_faces].upper()
                    y1,x2,y2,x1 = face_location
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, student_name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)  

            if ret:
                self.change_pixmap_signal.emit(img)

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.UI()
 
    def UI(self):
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
 
        page1 = HomeWindow(self)
        page1.login_btn.clicked.connect(self.check_window)
        # page1.signup_btn.clicked.connect(self.register_window)
        self.central_widget.addWidget(page1)        
 
        self.setGeometry(300, 100, 970, 670)
        # self.showMaximized()
        self.setWindowTitle('Attendance Checker')
        self.setWindowIcon(QIcon('C:\\Users\\ASUS\\Desktop\\atten\\campus.png'))
        self.setStyleSheet("background-color: darkgray;") 

    def check_window(self):
        page_check_window = Check_page(self)
        self.central_widget.addWidget(page_check_window)
        self.central_widget.setCurrentWidget(page_check_window)
    
    # def register_window(self):
    #     page_rt = Register_page(self)
    #     self.central_widget.addWidget(page_rt)
    #     self.central_widget.setCurrentWidget(page_rt)
 
class HomeWindow(QWidget):
    def __init__(self, parent=None):
        super(HomeWindow, self).__init__(parent)

        self.home_layout = QVBoxLayout()

        self.label = QLabel()
        font_label = QFont()
        font_label.setPointSize (30)
        font_label.setBold(True)
        self.label.setText('BME: ATTENDANCE CHECKER')
        self.label.setFont(font_label)
        self.label.setStyleSheet("background-color: black; color: white;")
        self.home_layout.addWidget(self.label)
        self.space_top_layout = QVBoxLayout()
        self.space_top = QLabel('   ')
        self.space_top_layout.addWidget(self.space_top)
        self.home_layout.addLayout(self.space_top_layout)

        font_btn = QFont()
        font_btn.setPointSize (14)
        self.btn_login = QPushButton('Log In')
        self.btn_login.setFont(font_btn)
        self.btn_login.setFixedSize(200,50)
        self.btn_login.setStyleSheet("background-color: white;")
        self.btn_signup = QPushButton('Sign Up')
        self.btn_signup.setFont(font_btn)
        self.btn_signup.setFixedSize(200,50)
        self.btn_signup.setStyleSheet("background-color: white;")
        self.login_btn = self.btn_login   
        self.signup_btn = self.btn_signup
        self.buttons_layout = QVBoxLayout() 
        self.buttons_layout.setAlignment(Qt.AlignCenter)
        self.buttons_layout.addWidget(self.btn_login)
        self.buttons_layout.addWidget(self.btn_signup)
        self.home_layout.addLayout(self.buttons_layout)

        self.space_bottom_layout = QVBoxLayout()
        self.space_bottom = QLabel('   ')
        self.space_bottom_layout.addWidget(self.space_bottom)
        self.home_layout.addLayout(self.space_bottom_layout)

        self.setLayout(self.home_layout)   

class Check_page(QMainWindow):
    def __init__(self, parent=None):
        super(Check_page, self).__init__(parent)
        self.UI()
 
    def UI(self):
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
 
        page2 = CheckWindow(self)
        # page2.back_btn.clicked.connect(self.back_homewindow)
        self.central_widget.addWidget(page2)
    
    # def back_homewindow(self):
    #     page_hw = Window(self)
    #     self.central_widget.addWidget(page_hw)
    #     self.central_widget.setCurrentIndex(self.central_widget.currentIndex()+1)

class CheckWindow(QWidget):
    def __init__(self, parent=None):
        super(CheckWindow, self).__init__(parent)

        self.image_label = QLabel(self)
        self.disply_width = 700
        self.display_height = 670
        self.image_label.resize(self.disply_width, self.display_height)

        # create a vertical box layout and add the two labels
        self.video_layout = QHBoxLayout()
        self.video_layout.addWidget(self.image_label)
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()
        self.video_widget = QWidget()
        self.video_widget.setLayout(self.video_layout)

        self.label = QLabel()
        font_time = QFont()
        font_time.setPointSize (14)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font_time)
        self.time_layout = QHBoxLayout()
        self.time_layout.addWidget(self.label)
        self.time_widget = QWidget()
        self.time_widget.setLayout(self.time_layout)
        timer = QTimer(self)
        timer.timeout.connect(self.show_time)
        timer.start(1000)

        self.splitter1 = QSplitter(Qt.Horizontal)
        self.splitter1.addWidget(self.video_widget)
        self.splitter1.addWidget(self.time_widget)
        self.splitter1.setStretchFactor(1, 1)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.splitter1)
        self.setLayout(self.layout)
    
    def show_time(self):
        current_time = QTime.currentTime()
        label_time = current_time.toString('hh:mm:ss')
        self.label.setText(label_time)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()
    
    @pyqtSlot(np.ndarray)
    def update_image(self, img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec_()