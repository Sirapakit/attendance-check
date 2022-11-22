from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime

SERVICE_ACCOUNT_FILE = 'key.json'
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

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
name = [["Pim","6213424",checkin_str]]

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

