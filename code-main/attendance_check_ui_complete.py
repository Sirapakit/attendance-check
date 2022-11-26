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
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

import numpy as np
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import json
import time

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    current_status = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # path = r'../image'
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
            status = False
            img_from_webcam = cv2.resize(img, (0, 0), None, fx = 0.25, fy = 0.25)

            img_from_webcam = cv2.cvtColor(img_from_webcam, cv2.COLOR_BGR2RGB)

            faces_current_frame = face_recognition.face_locations(img_from_webcam)
            encodes_current_frame = face_recognition.face_encodings(img_from_webcam, faces_current_frame) # in case many faces, send face location

            for encode_face, face_location in zip(encodes_current_frame, faces_current_frame):
                matches = face_recognition.compare_faces(encode_list_registered_faces, encode_face)
                face_distance = face_recognition.face_distance(encode_list_registered_faces, encode_face)
                match_faces = np.argmin(face_distance)

                if matches[match_faces]:
                    student_name = class_name[match_faces]
                    y1,x2,y2,x1 = face_location
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, student_name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2) 
                    status = True

            if ret:
                self.change_pixmap_signal.emit(img)
                self.current_status.emit(status)
            
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class CaptureThread(QThread):
    capture_image = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        camera = cv2.VideoCapture(0)
        while True:
            ret, frame = camera.read()
            frame = cv2.flip(frame,1)
            font = cv2.FONT_HERSHEY_TRIPLEX
            cv2.putText(frame, 'Front Face', (50, 50), font, 1, (255, 255, 255), 2, cv2.LINE_4)

            if ret:
                self.capture_image.emit(frame)
    
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
        page1.signup_btn.clicked.connect(self.register_window)
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
    
    def register_window(self):
        page_rt = Register_page(self)
        self.central_widget.addWidget(page_rt)
        self.central_widget.setCurrentWidget(page_rt)
 
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
        page2.back_btn.clicked.connect(self.back_homewindow)
        self.central_widget.addWidget(page2)


    def back_homewindow(self):
        page_hw = Window(self)
        self.central_widget.addWidget(page_hw)
        self.central_widget.setCurrentIndex(self.central_widget.currentIndex()+1)

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
        self.thread.current_status.connect(self.show_status)
        # self.thread.student_name_signal.connect(self.check_attendance)
        self.thread.start()
        self.video_widget = QWidget()
        self.video_widget.setLayout(self.video_layout)

        self.label = QLabel()
        font_time = QFont()
        font_time.setPointSize (17)
        font_time.setBold = True
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font_time)
        self.time_layout = QVBoxLayout()
        self.time_layout.addWidget(self.label)
        self.right_widget = QWidget()
        self.right_widget.setLayout(self.time_layout)
        timer = QTimer(self)
        timer.timeout.connect(self.show_time)
        timer.start(1000)

        self.name_layout = QHBoxLayout()
        font_name = QFont()
        font_name.setPointSize(14)
        self.name_label = QLabel('Name:')
        self.name_label.setFont(font_name)
        self.name_textbox = QLineEdit()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_textbox)
        self.time_layout.addLayout(self.name_layout)

        self.status = False
        font_status = QFont()
        font_status.setPointSize(17)
        font_status.setBold = True
        self.status_layout = QVBoxLayout()
        self.status_label = QLabel('Status')
        self.status_label.setFont(font_status)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_show = QLabel('WAITING', self)
        self.status_show.setFont(font_status)
        self.status_show.setStyleSheet("background-color: black; color: white;")
        self.status_show.setAlignment(Qt.AlignCenter)
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.status_show)
        self.time_layout.addLayout(self.status_layout)

        font_btn = QFont()
        font_btn.setPointSize(14)
        self.btn_enter = QPushButton('ENTER')
        self.btn_enter.setFont(font_btn)
        self.btn_enter.setStyleSheet("background-color: lightskyblue;")
        self.btn_enter.clicked.connect(self.clicked_enter)
        self.btn_back = QPushButton('BACK')
        self.btn_back.setFont(font_btn)
        self.btn_back.setStyleSheet("background-color: lightpink;")
        self.enter_btn = self.btn_enter
        self.back_btn = self.btn_back
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(self.btn_enter)
        self.buttons_layout.addWidget(self.btn_back)
        self.time_layout.addLayout(self.buttons_layout)

        self.splitter1 = QSplitter(Qt.Horizontal)
        self.splitter1.addWidget(self.video_widget)
        self.splitter1.addWidget(self.right_widget)
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

    @pyqtSlot(bool)
    def show_status(self, status):
        if (status):
            self.status = True
            self.status_show.setText('DETECTED')
        else:
            self.status = False
            self.status_show.setText('WAITING')
    
    def clicked_enter(self):
        self.check_attendance()

    def check_attendance(self):

        def get_student_id_from_json(name):
            f = open('student_id.json')
            data = json.load(f)
            return data[name]

        SERVICE_ACCOUNT_FILE = 'key.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        creds = None
        creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        SAMPLE_SPREADSHEET_ID = '1jnApnXnB3yq4qSX_VkjU04jykh_Aj4ggDTJHMhqsYyY'
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        sheet_id = 0
        head = [["Name","ID","Time"]]

        request_body_head =  \
        {
        "requests": [
            {
            "repeatCell": {
                "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": 1
                },
                "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                    "red": 1.0,
                    "green": 1.0,
                    "blue": 1.0
                    },
                    "horizontalAlignment" : "CENTER",
                    "textFormat": {
                    "foregroundColor": {
                        "red": 0.0,
                        "green": 0.0,
                        "blue": 0.0
                    },
                    "fontSize": 10,
                    "bold": True
                    }
                }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
            }
        ]
        }


        request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet 1!A1", valueInputOption="USER_ENTERED", body={"values":head}).execute()
        respond = sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=request_body_head).execute()

        checkin = datetime.datetime.now()
        ontime = checkin.replace(hour=9, minute=0, second=0, microsecond=0)
        # test = checkin.replace(hour=9, minute=0, second=0, microsecond=0)
        checkin_str = checkin.strftime("%H:%M:%S")

        student_name = self.name_textbox.text()
        student_id = get_student_id_from_json(student_name)
        name = [[student_name,student_id,checkin_str]]

        append = sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet 1!A2:C", valueInputOption="USER_ENTERED", 
                    insertDataOption="INSERT_ROWS",responseDateTimeRenderOption="FORMATTED_STRING", body={"values":name}).execute()
        if checkin - ontime > datetime.timedelta(minutes = 15): # 15 mins
            row = 1
            last_row = 2
            respond_last_row = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet 1!C2:C").execute()
            row += len(respond_last_row['values'])
            last_row += len(respond_last_row['values'])

            request_late =  \
                {
                "requests": [
                    {
                    "repeatCell": {
                        "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row,
                    "endRowIndex": last_row
                    },
                        "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 1.0
                            },
                            "horizontalAlignment" : "CENTER",
                            "textFormat": {
                            "foregroundColor": {
                                "red": 1.0,
                                "green": 0.0,
                                "blue": 0.0
                            },
                            "fontSize": 10,
                            "bold": False
                            }
                        }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                    }
                    }
                ]
                }
            respond_late = sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=request_late).execute()

        else:
            row = 1
            last_row = 2
            find_last_row = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet 1!A2:C").execute()
            row += len(find_last_row['values']) - 1
            last_row += len(find_last_row['values']) - 1

            request_ontime =  \
                {
                "requests": [
                    {
                    "repeatCell": {
                        "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row,
                    "endRowIndex": last_row
                    },
                        "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 1.0
                            },
                            "horizontalAlignment" : "CENTER",
                            "textFormat": {
                            "foregroundColor": {
                                "red": 0.0,
                                "green": 0.0,
                                "blue": 0.0
                            },
                            "fontSize": 10,
                            "bold": False
                            }
                        }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                    }
                    }
                ]
                }
            respond_late = sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=request_ontime).execute()
        sys.exit()

class Register_page(QMainWindow):
    def __init__(self, parent=None):
        super(Register_page, self).__init__(parent)
        self.UI()
 
    def UI(self):
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
 
        page3 = RegisterWindow(self)
        page3.submit_btn.clicked.connect(self.back_homewindow)
        self.central_widget.addWidget(page3)        
      
    def back_homewindow(self):
        page_hw = Window(self)
        self.central_widget.addWidget(page_hw)
        self.central_widget.setCurrentIndex(self.central_widget.currentIndex()+1)

class RegisterWindow(QWidget):
    def __init__(self, parent=None):
        super(RegisterWindow, self).__init__(parent)

        self.image_label = QLabel(self)
        self.disply_width = 700
        self.display_height = 670
        self.image_label.resize(self.disply_width, self.display_height)

        self.capture = False
        self.btn_capture = QPushButton('Capture')
        self.btn_capture.clicked.connect(self.capture_clicked)

        # create a vertical box layout and add the two labels
        self.video_layout = QVBoxLayout()
        self.video_layout.addWidget(self.image_label)
        self.video_layout.addWidget(self.btn_capture)
        self.thread = CaptureThread()
        self.thread.capture_image.connect(self.update_image)
        self.thread.capture_image.connect(self.register_new_student)
        self.thread.start()
        self.video_widget = QWidget()
        self.video_widget.setLayout(self.video_layout)

        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout()
        self.name_layout = QHBoxLayout()
        font_name = QFont()
        font_name.setPointSize(14)
        self.name_label = QLabel('Name:')
        self.name_label.setFont(font_name)
        self.name_textbox = QLineEdit()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_textbox)
        self.right_layout.addLayout(self.name_layout)
        self.id_layout = QHBoxLayout()
        self.id_label = QLabel('Student ID:')
        self.id_label.setFont(font_name)
        self.id_textbox = QLineEdit()
        self.id_layout.addWidget(self.id_label)
        self.id_layout.addWidget(self.id_textbox)
        self.right_layout.addLayout(self.id_layout)
        self.right_widget.setLayout(self.right_layout)

        self.btn_layout = QVBoxLayout()
        font_btn = QFont()
        font_btn.setPointSize(14)
        self.btn_submit = QPushButton('Submit')
        self.btn_submit.setFont(font_btn)
        self.btn_submit.setStyleSheet("background-color: white;")
        self.submit_btn = self.btn_submit
        self.btn_layout.addWidget(self.btn_submit)
        self.right_layout.addLayout(self.btn_layout)

        self.splitter1 = QSplitter(Qt.Horizontal)
        self.splitter1.addWidget(self.video_widget)
        self.splitter1.addWidget(self.right_widget)
        self.splitter1.setStretchFactor(1, 1)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.splitter1)
        self.setLayout(self.layout)
    
    
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
    
    def capture_clicked(self):
        self.capture = True

    def register_new_student(self, frame):
        def write_json(student_name, student_id, filename='student_id.json'):
            with open(filename,'r+') as file:
                file_data = json.load(file)
                file_data[student_name] = student_id
                file.seek(0)
                json.dump(file_data, file, indent = 4)

        if self.capture:
            filename = 'C:\\Users\\ASUS\\Desktop\\atten\\image\\' + self.name_textbox.text() + '.jpg'
            cv2.imwrite(filename, img = frame)
            write_json(student_name=self.name_textbox.text(), student_id=self.id_textbox.text())
            print('completely captured image..')
            self.capture = False
        
   
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec_()