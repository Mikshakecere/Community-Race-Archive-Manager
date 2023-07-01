import os
import math

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def main():
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
        """
        step 1: get dictionary with all top 3 amounts and names 
        step 2: sort dictionary
        step 3: add to top 3 column
        """
        #creates dictionary and searches for names to find players and their amounts of t3
        place = {}
        row = 8
        value = str(sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=f"Races!K{row}").execute().get("values")[0][0])

        while(row != 14):
            if value == "N/A":
                row += 2
                value = str(sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=f"Races!K{row}").execute().get("values")[0][0])
                continue
            elif value not in place:
                place[value] = 1
            else:
                place[value] += 1

            #iterates to the next row
            row += 2
            value = str(sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=f"Races!K{row}").execute().get("values")[0][0])

        print(place)
        sorted_place = sorted(place.items(),key=lambda x:x[1])
        print(sorted_place)




    except HttpError as error:
        print(error)

"""
def numberEdit(startingNum, startingRow, endingRow):
    count = startingNum
    for row in range(startingRow, endingRow-1, 2):
        sheets.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Races!B{row}", valueInputOption="USER_ENTERED",
                               body={"values": [[f"{count}"]]}).execute()
        count += 1
"""

"""
this will sort the top 3 placement columns based on amount
i should have this automate every 24 hrs or something but that would require leaving pc on n shit. idk though
also should attempt to link races and top 3 pages, using the races sheet as information input 
THESE DONT WORK AS FUNCTIONS im stupid
"""

if __name__ == "__main__":
    main()