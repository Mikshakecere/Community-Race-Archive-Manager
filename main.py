import os
import math

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
        """
        step 1: get dictionary with all top 3 amounts and names/ partly, nonetype case still needs managing but n/a will be placeholder. also id like to figure out a way to batch get every name
        step 2: sort dictionary/ finished
        step 3: add to top 3 column/ finished
            3.1: update all of top 3 at the same time
            3.2: update the border formatting to correspond with updated placements
        """
        #creates dictionary and searches for names to find players and their amounts of t3
        place = {}
        row = 8
        value = str(sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=f"Races!K{row}").execute().get("values")[0][0])

        while(value != "no data"):
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

        #sorting dictionary
        sorted_place = dict(sorted(sorted(place.items(),key=lambda x:x[1])))

        #add sorted dict to top3 sheet
        row = 7
        for x,y in sorted_place.items():
            sheets.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Top 3!B{row}",
                                   valueInputOption="USER_ENTERED", body={"values": [[x]]}).execute()
            sheets.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Top 3!D{row}",
                                   valueInputOption="USER_ENTERED", body={"values": [[y]]}).execute()
            row += 1

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
#i should have this automate every 24 hrs or something but that would require leaving pc on n shit. idk though

if __name__ == "__main__":
    main()