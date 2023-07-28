from datetime import date
import threading
#i need to learn how to use threading

class SheetsManager:
    def __init__(self, sheets, ssid):
        self.sheets = sheets
        self.ssid = ssid

    def lb_to_t3(self) -> None:
        print("Checking for newer data")
        latest = self.sheets.values().get(spreadsheetId=self.ssid,
                                     range=f"Top 3!B4").execute().get("values")[0][0]
        latest = int(latest[-1:])+1
        row = 2*(latest-1)+8
        try:
            check = self.sheets.values().get(spreadsheetId=self.ssid,
                                     range=f"Leaderboard!K{row}").execute().get("values")[0][0]
        except TypeError:
            print(latest)
            print("There is no new data to be processed. Terminating lb_to_t3 method")
            return None

        print("Creating dictionary and processing leaderboard data...")
        places = {
            "placeF": {},
            "placeS": {},
            "placeT": {}
        }

        letters = ["F","S","T"]
        index = 0

        #this will only run for 3 columns, but each column is indefinite amounts long, therefore use for and while
        print("Looping through columns")
        for i in range(66,73,3):
            row = 10
            while (True):
                try:
                    name = self.sheets.values().get(spreadsheetId=self.ssid,
                                                      range=f"Top 3!{chr(i)}{row}").execute().get("values")[0][0]
                    amount = self.sheets.values().get(spreadsheetId=self.ssid,
                                                      range=f"Top 3!{chr(i + 2)}{row}").execute().get("values")[0][0]
                    places[f"place{letters[index]}"][name] = int(amount)
                    row += 1
                except TypeError:
                    index += 1
                    break

        row = 2*(latest-1)+8
        valueF = self.sheets.values().get(spreadsheetId=self.ssid,
                                     range=f"Leaderboard!K{row}").execute().get("values")[0][0]
        valueS = self.sheets.values().get(spreadsheetId=self.ssid,
                                     range=f"Leaderboard!M{row}").execute().get("values")[0][0]
        valueT = self.sheets.values().get(spreadsheetId=self.ssid,
                                     range=f"Leaderboard!O{row}").execute().get("values")[0][0]
        count = 0

        for i in letters:
            print(places[f"place{i}"])

        while (True):
            count += 1
            places = self.dict_update(valueF, places, "F")
            places = self.dict_update(valueS, places, "S")
            places = self.dict_update(valueT, places, "T")
            try:
                row += 2
                valueF = self.sheets.values().get(spreadsheetId=self.ssid,
                                             range=f"Leaderboard!K{row}").execute().get("values")[0][0]
                valueS = self.sheets.values().get(spreadsheetId=self.ssid,
                                             range=f"Leaderboard!M{row}").execute().get("values")[0][0]
                valueT = self.sheets.values().get(spreadsheetId=self.ssid,
                                             range=f"Leaderboard!O{row}").execute().get("values")[0][0]
            except TypeError:
                latest = self.sheets.values().get(spreadsheetId=self.ssid,
                                             range=f"Leaderboard!B{row-2}").execute().get("values")[0][0]
                break

        print(count)

        print("Sorting dictionary...")
        places["placeF"] = dict(sorted(places["placeF"].items(), key=lambda x:x[1], reverse=True))
        places["placeS"] = dict(sorted(places["placeS"].items(), key=lambda x:x[1], reverse=True))
        places["placeT"] = dict(sorted(places["placeT"].items(), key=lambda x:x[1], reverse=True))
        print("Dictionary successfully sorted in descending order")

        print("Updating total Top 3...")
        self.top_3_updater(places, 10, latest)

    def dict_update(self, value, places, place) -> dict:
        if value == "N/A":
            pass
        elif value not in places[f"place{place}"]:
            places[f"place{place}"][value] = 1
        else:
            places[f"place{place}"][value] += 1
        return places

    def top_3_updater(self, places, row,latest) -> None:
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
                               body={"values": [[f"Last Updated: Race #{latest}"]]}).execute()

    def numberEdit(self, starting_num, starting_row, ending_row) -> None:
        count = starting_num
        for row in range(starting_row, ending_row - 1, 2):
            self.sheets.values().update(spreadsheetId=self.ssid, range=f"Leaderboard!B{row}", valueInputOption="USER_ENTERED",
                                   body={"values": [[f"{count}"]]}).execute()
            count += 1

    # check where the last race name before none type is and then take both name and race num
    # go to the race ranking sheet and see where the race needs to be updated to
    # only take races from last updated on race ranking to last updated on race lb
    # f"Race #{race_number}: \"{race_name}\" by {race_creator}"
    def lb_to_ranking(self) -> None:
        print("")