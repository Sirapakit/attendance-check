import cv2
import numpy as np
import face_recognition

img_pung = face_recognition.load_image_file('../image/pung3.jpg')
img_pung = cv2.cvtColor(img_pung, cv2.COLOR_BGR2RGB)

img_pung_test = face_recognition.load_image_file('../image/pung1.jpg')
img_pung_test = cv2.cvtColor(img_pung_test, cv2.COLOR_BGR2RGB)

face_loc = face_recognition.face_locations(img_pung)[0] # return coord of face
encode_pung = face_recognition.face_encodings(img_pung)[0]
cv2.rectangle(img_pung, (face_loc[3], face_loc[0]), (face_loc[1], face_loc[2]), (0, 255, 0), 3)

face_loc_test = face_recognition.face_locations(img_pung_test)[0] # return coord of face
encode_pung_test = face_recognition.face_encodings(img_pung_test)[0]
cv2.rectangle(img_pung_test, (face_loc[3], face_loc[0]), (face_loc[1], face_loc[2]), (0, 255, 0), 3)

results = face_recognition.compare_faces([encode_pung], encode_pung_test) # return boolean
face_distance = face_recognition.face_distance([encode_pung], encode_pung_test) # return percentage ( high = bad )
cv2.putText(img_pung_test, f'{results} {round(face_distance[0],2)}', (60,60), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)

cv2.imshow('Pung', img_pung_test)
cv2.imshow('Pung2', img_pung)
cv2.waitKey(0)