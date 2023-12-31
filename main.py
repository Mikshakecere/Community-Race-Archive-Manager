import os
import time
from SheetsManager import SheetsManager

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def main():
    #boiler plate
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SPREADSHEET_ID = "1A9FnmWrgeNvR9zpThAdRLiBzq9XlxWuVupCSDSDtbLo"
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    try:
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()
        sm = SheetsManager(sheets,SPREADSHEET_ID)

        #add option to redo top 3 from scratch in case i fucked up rankings
        #updates top 3 sheet using data from leaderboard
        action = input("Available commands: 'top3', 'resett3', 'rowadd'")

        start = time.time()
        if action == 'top3':
            sm.lb_to_t3()
        elif action == 'resett3':
            #i still need to implement this shit ahaahhahahahhaha
            sm.lb_to_t3()
        elif action == 'rowadd':
            sm.row_add()
            #sm.row_add(5,16,107)
        else:
            print("call the function thing again")

        end = time.time()
        print("Program successful! Runtime:", (end - start) * 10 ** 3, "ms")

    except HttpError as error:
        print(error)

if __name__ == "__main__":
    main()