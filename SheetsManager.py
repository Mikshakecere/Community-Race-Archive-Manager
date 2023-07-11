from datetime import date
import threading

class SheetsManager:
    def __init__(self, sheets, ssid):
        self.sheets = sheets
        self.ssid = ssid

    def lb_to_t3(self) -> None:
        print("Creating dictionary and processing leaderboard data...")
        places = {
            "placeF": {},
            "placeS": {},
            "placeT": {}
        }
        row = 8
        valueF = self.sheets.values().get(spreadsheetId=self.ssid,
                                     range=f"Leaderboard!K{row}").execute().get("values")[0][0]
        valueS = self.sheets.values().get(spreadsheetId=self.ssid,
                                     range=f"Leaderboard!M{row}").execute().get("values")[0][0]
        valueT = self.sheets.values().get(spreadsheetId=self.ssid,
                                     range=f"Leaderboard!O{row}").execute().get("values")[0][0]

        while (True):
            if valueF == "N/A":
                pass
            elif valueF not in places["placeF"]:
                places["placeF"][valueF] = 1
            else:
                places["placeF"][valueF] += 1

            if valueS == "N/A":
                pass
            elif valueS not in places["placeS"]:
                places["placeS"][valueS] = 1
            else:
                places["placeS"][valueS] += 1

            if valueT == "N/A":
                pass
            elif valueT not in places["placeT"]:
                places["placeT"][valueT] = 1
            else:
                places["placeT"][valueT] += 1

            try:
                row += 2
                valueF = self.sheets.values().get(spreadsheetId=self.ssid,
                                             range=f"Leaderboard!K{row}").execute().get("values")[0][0]
                valueS = self.sheets.values().get(spreadsheetId=self.ssid,
                                             range=f"Leaderboard!M{row}").execute().get("values")[0][0]
                valueT = self.sheets.values().get(spreadsheetId=self.ssid,
                                             range=f"Leaderboard!O{row}").execute().get("values")[0][0]
            except TypeError:
                break

        print("Sorting dictionary...")
        places["placeF"] = dict(sorted(places["placeF"].items(), key=lambda x: x[1], reverse=True))
        places["placeS"] = dict(sorted(places["placeS"].items(), key=lambda x: x[1], reverse=True))
        places["placeT"] = dict(sorted(places["placeT"].items(), key=lambda x: x[1], reverse=True))
        print("Dictionary successfully sorted in descending order")

        print("Updating total Top 3...")
        self.top_3_updater(places, 10)

    def top_3_updater(self, places, row) -> None:
        col = 66
        row_original = row
        for d in places:
            row = row_original
            for k in places[d].keys():
                self.sheets.values().update(spreadsheetId=self.ssid, range=f"Top 3!{chr(col)}{row}",
                                       valueInputOption="USER_ENTERED", body={"values": [[k]]}).execute()
                row += 1
            row = row_original
            for v in places[d].values():
                self.sheets.values().update(spreadsheetId=self.ssid, range=f"Top 3!{chr(col + 2)}{row}",
                                       valueInputOption="USER_ENTERED", body={"values": [[v]]}).execute()
                row += 1
            col += 3
        self.sheets.values().update(spreadsheetId=self.ssid, range=f"Top 3!B4",
                               valueInputOption="USER_ENTERED",
                               body={"values": [[f"Last Updated: {date.today()}"]]}).execute()

    def numberEdit(self, starting_num, starting_row, ending_row) -> None:
        count = starting_num
        for row in range(starting_row, ending_row - 1, 2):
            self.sheets.values().update(spreadsheetId=self.ssid, range=f"Leaderboard!B{row}", valueInputOption="USER_ENTERED",
                                   body={"values": [[f"{count}"]]}).execute()
            count += 1
