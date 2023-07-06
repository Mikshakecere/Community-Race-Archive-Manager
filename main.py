import os
import time
from datetime import date

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
        step 1: get dictionary with all top 3 amounts and names/ partly, nonetype case still needs managing but no data can be placeFholder. 
                also id like to figure out a way to batch get every name instead of individually with while loop and +2 but idk how to do that
        step 2: sort dictionary/ finished
        step 3: add to top 3 column/ finished
            3.1: update all of top 3 at the same time/ finished
            3.2: update the border formatting to correspond with updated placements/ thats too much effort :D
            3.3: optimize runtime it sucks
        """
        start = time.time()
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

        while(True):
            if valueF == "N/A": pass
            elif valueF not in places["placeF"]: places["placeF"][valueF] = 1
            else: places["placeF"][valueF] += 1

            if valueS == "N/A": pass
            elif valueS not in places["placeS"]: places["placeS"][valueS] = 1
            else: places["placeS"][valueS] += 1

            if valueT == "N/A": pass
            elif valueT not in places["placeT"]: places["placeT"][valueT] = 1
            else: places["placeT"][valueT] += 1

            try:
                row += 2
                valueF = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                                             range=f"Races!K{row}").execute().get("values")[0][0]
                valueS = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                                             range=f"Races!M{row}").execute().get("values")[0][0]
                valueT = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                                             range=f"Races!O{row}").execute().get("values")[0][0]
            except TypeError:
                break

        print("Sorting dictionary...")
        places["placeF"] = dict(sorted(places["placeF"].items(),key=lambda x:x[1],reverse=True))
        places["placeS"] = dict(sorted(places["placeS"].items(),key=lambda x:x[1],reverse=True))
        places["placeT"] = dict(sorted(places["placeT"].items(),key=lambda x:x[1],reverse=True))
        print("Dictionary successfully sorted in descending order")

        print("Updating total Top 3...")
        top_3_updater(sheets, places, SPREADSHEET_ID, 10)

        end = time.time()
        print("Program successful! Runtime:", (end - start) * 10 ** 3, "ms")

    except HttpError as error:
        print(error)

def top_3_updater(sheets, places, ss_id, row):
    col = 66
    row_original = row
    for d in places:
        row = row_original
        for k in places[d].keys():
            sheets.values().update(spreadsheetId=ss_id, range=f"Top 3!{chr(col)}{row}",
                                   valueInputOption="USER_ENTERED", body={"values": [[k]]}).execute()
            row += 1
        row = row_original
        for v in places[d].values():
            sheets.values().update(spreadsheetId=ss_id, range=f"Top 3!{chr(col + 2)}{row}",
                                   valueInputOption="USER_ENTERED", body={"values": [[v]]}).execute()
            row += 1
        col += 3
    sheets.values().update(spreadsheetId=ss_id, range=f"Top 3!B4",
                           valueInputOption="USER_ENTERED", body={"values": [[f"Last Updated: {date.today()}"]]}).execute()


def numberEdit(starting_num, starting_row, ending_row, sheets, ss_id):
    count = starting_num
    for row in range(starting_row, ending_row-1, 2):
        sheets.values().update(spreadsheetId=ss_id, range=f"Races!B{row}", valueInputOption="USER_ENTERED",
                               body={"values": [[f"{count}"]]}).execute()
        count += 1


if __name__ == "__main__":
    main()