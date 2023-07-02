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
        step 1: get dictionary with all top 3 amounts and names/ partly, nonetype case still needs managing but n/a will be placeFholder. also id like to figure out a way to batch get every name
        step 2: sort dictionary/ finished
        step 3: add to top 3 column/ finished
            3.1: update all of top 3 at the same time/ finished
            3.2: update the border formatting to correspond with updated placements
        """
        print("Creating dictionary and processing leaderboard data...")
        places = {
            "placeF": {},
            "placeS": {},
            "placeT": {}
        }


        row = 8
        valueF = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                                     range=f"Races!K{row}").execute().get("values")[0][0]
        valueS = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                                     range=f"Races!M{row}").execute().get("values")[0][0]
        valueT = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                                     range=f"Races!O{row}").execute().get("values")[0][0]

        while(valueF != "no data"):
            if valueF == "N/A": pass
            elif valueF not in places["placeF"]: places["placeF"][valueF] = 1
            else: places["placeF"][valueF] += 1

            if valueS == "N/A": pass
            elif valueS not in places["placeS"]: places["placeS"][valueS] = 1
            else: places["placeS"][valueS] += 1

            if valueT == "N/A": pass
            elif valueT not in places["placeT"]: places["placeT"][valueT] = 1
            else: places["placeT"][valueT] += 1

            print("Iterating to row " + str(row) + "...")
            row += 2
            valueF = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                                         range=f"Races!K{row}").execute().get("values")[0][0]
            valueS = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                                         range=f"Races!M{row}").execute().get("values")[0][0]
            valueT = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                                         range=f"Races!O{row}").execute().get("values")[0][0]

        print("Sorting dictionary...")
        places["placeF"] = dict(sorted(places["placeF"].items(),key=lambda x:x[1],reverse=True))
        places["placeS"] = dict(sorted(places["placeS"].items(),key=lambda x:x[1],reverse=True))
        places["placeT"] = dict(sorted(places["placeT"].items(),key=lambda x:x[1],reverse=True))
        print("Dictionary successfully sorted in descending order")

        print("Updating total Top 3...")
        col = 0
        colsK = ("B","E","H")
        colsV = ("D","G","J")
        for d in places:
            row = 7
            for k in places[d].keys():
                sheets.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Top 3!{colsK[col]}{row}",
                                       valueInputOption="USER_ENTERED", body={"values": [[k]]}).execute()
                row += 1
            row = 7
            for v in places[d].values():
                sheets.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Top 3!{colsV[col]}{row}",
                                       valueInputOption="USER_ENTERED", body={"values": [[v]]}).execute()
                row += 1
            col += 1

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

if __name__ == "__main__":
    main()