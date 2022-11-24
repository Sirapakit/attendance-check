import cv2
import numpy as np
import face_recognition
import os 
from datetime import datetime as datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime
import json

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


def get_student_id_from_json(name):
    f = open('student_id.json')
    data = json.load(f)
    return data[name]

student_id = get_student_id_from_json('pung')
print(f'Hi, {student_id}')

def register_new_student():
    name = input('name: ')
    camera = cv2.VideoCapture(0)
    while True:
        ret, frame = camera.read()
        frame = cv2.flip(frame,1)
        font = cv2.FONT_HERSHEY_TRIPLEX
        cv2.putText(frame, 'Front Face', (50, 50), font, 1, (255, 255, 255), 2, cv2.LINE_4)
        cv2.imshow('camera', frame)

        key = cv2.waitKey(1)
        if key == ord('c'):
            filename = '../image/' + name + '.jpg'
            cv2.imwrite(filename, img = frame)
            print('completely captured image..')
            break
        elif key == ord('q'):
            print('non captured image')
            break
    camera.release()
    # cv2.destroyAllWindows()


def find_encodings(images):
    encode_list = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encode_list.append(encode)
    return encode_list

encode_list_registered_faces = find_encodings(images)
# print(encode_list_registered_faces)
print('Encodings Complete!')

def check_attendance(name):
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

    student_id = get_student_id_from_json(name)
 
    name = [[name, student_id, checkin_str]]

    append = sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet 1!A2", valueInputOption="USER_ENTERED", 
                insertDataOption="INSERT_ROWS",responseDateTimeRenderOption="FORMATTED_STRING", body={"values":name}).execute()
    if checkin - ontime > datetime.timedelta(minutes = 15): # 15 mins
        row = 1
        last_row = 2
        respond_last_row = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet 1!A2:C").execute()
        row += len(respond_last_row['values']) - 1
        last_row += len(respond_last_row['values']) - 1

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

# Main Code Here
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

        if matches[match_faces]: # Detect faces
            student_name = class_name[match_faces]
            y1,x2,y2,x1 = face_location
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, student_name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
            if cv2.waitKey(1) & 0xFF == ord('s'):
                check_attendance(student_name)
    cv2.imshow('Webcam',img)

    if cv2.waitKey(1) & 0xFF == ord('p'):
        cap.release()
        register_new_student()
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # cap.release()