import cv2
import numpy as np
import face_recognition
import os 
from datetime import datetime as datetime

path = r'../image'
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
print('Encodings Complete!')

def check_attendance(name):
    with open('atten.csv','r+') as f:
        my_datalist = f.readlines()
        student_name_list = []
        for line in my_datalist:
            entry = line.split(',')
            student_name_list.append(entry[0])
        if name not in student_name_list:
            now = datetime.now()
            dt_string = now.strftime("%H:%M:%S")
            f.writelines(f'n{name},{dt_string}\n')

# Webcam
cap = cv2.VideoCapture(0)
while True:
    success, img = cap.read()
    img_from_webcam = cv2.resize(img, (0, 0), None, fx = 0.25, fy = 0.25)
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
            check_attendance(student_name)

    cv2.imshow('Webcam',img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # cap.release()