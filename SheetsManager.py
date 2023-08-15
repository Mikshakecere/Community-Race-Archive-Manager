import multiprocessing
import time
#i need to learn how to use threading

class SheetsManager:
    def __init__(self, sheets, ssid):
        self.sheets = sheets
        self.ssid = ssid

    def lb_to_t3(self) -> None:
        """

        :return:
        """
        print("Checking for newer data")
        latest = self.sheets.values().get(spreadsheetId=self.ssid,
                                          range=f"Top 3!B4").execute().get("values")[0][0]
        latest = int(latest[-1:])+1
        row = 2*(latest-1)+8
        try:
            self.sheets.values().get(spreadsheetId=self.ssid,
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

        print("Looping through columns")

        #use a batch get instead
        """thing = self.sheets.values().batchGet(spreadsheetId=self.ssid,
                                              ranges=f"Top3!B10:C15").execute()
        print(thing)"""

        row = 2*(latest-1)+8
        valueF = self.sheets.values().get(spreadsheetId=self.ssid,
                                          range=f"Leaderboard!K{row}").execute().get("values")[0][0]
        valueS = self.sheets.values().get(spreadsheetId=self.ssid,
                                          range=f"Leaderboard!M{row}").execute().get("values")[0][0]
        valueT = self.sheets.values().get(spreadsheetId=self.ssid,
                                          range=f"Leaderboard!O{row}").execute().get("values")[0][0]

        while (True):
            #try to put valueFST into values list and have places dicts be updated
            places["placeF"] = self.dict_update(valueF, places, "F")
            places["placeS"] = self.dict_update(valueS, places, "S")
            places["placeT"] = self.dict_update(valueT, places, "T")

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

        print("Sorting dictionary...")
        for place in places:
            places[place] = dict(sorted(places[place].items(), key=lambda x:x[1], reverse=True))

        for place in places.items():
            print(place)

        print("Updating total Top 3...")

        u1 = multiprocessing.Process(target=self.top_3_updater,args=(places["placeF"],66))
        u2 = multiprocessing.Process(target=self.top_3_updater,args=(places["placeS"],69))
        u3 = multiprocessing.Process(target=self.top_3_updater,args=(places["placeT"],72))

        u1.start()
        u2.start()
        u3.start()

        u1.join()
        u2.join()
        u3.join()

        self.sheets.values().update(spreadsheetId=self.ssid, range=f"Top 3!B4", valueInputOption="USER_ENTERED",
                                    body={"values": [[f"Last Updated: Race #{latest}"]]}).execute()

    def dict_update(self, value, places, place) -> dict:
        """
        dict_update

        :param value: value will typically be
        :param places:
        :return: dictionary places[placex]
        """
        if value == "N/A":
            pass
        elif value not in places[f"place{place}"]:
            places[f"place{place}"][value] = 1
        else:
            places[f"place{place}"][value] += 1
        return places[f"place{place}"]

    def top_3_updater(self, place, col) -> None:
        """
        top_3_updater will update the sheet "Top 3" with the new information in the dictionary 'places'

        :param place: dictionary of dictionaries to have information accessed and used to update the sheet "Top 3"
        :param row: value that remains unchanged in order to be able to move on to the next column
        :param latest: value to update the last updated text using the latest row with info
        """
        row_iter = 10
        for k in place.keys():
            self.sheets.values().update(spreadsheetId=self.ssid, range=f"Top 3!{chr(col)}{row_iter}", valueInputOption="USER_ENTERED",
                                        body={"values": [[k]]}).execute()
            row_iter += 1
        row_iter = 10
        for v in place.values():
            self.sheets.values().update(spreadsheetId=self.ssid, range=f"Top 3!{chr(col + 2)}{row_iter}", valueInputOption="USER_ENTERED",
                                        body={"values": [[v]]}).execute()
            row_iter += 1


    def row_add(self, starting_num, starting_row, ending_row) -> None:
        """
        row_add

        :param starting_num:
        :param starting_row:
        :param ending_row:
        :return:
        """
        count = starting_num
        for row in range(starting_row, ending_row - 1, 2):
            self.sheets.values().update(spreadsheetId=self.ssid, range=f"Leaderboard!B{row}", valueInputOption="USER_ENTERED",
                                        body={"values": [[f"{count}"]]}).execute()
            count += 1

    """check where the last race name before none type is and then take both name and race num
    go to the race ranking sheet and see where the race needs to be updated to
    only take races from last updated on race ranking to last updated on race lb
    f"Race #{race_number}: \"{race_name}\" by {race_creator}"""
    def lb_to_ranking(self) -> None:
        print("")

    """im pretty sure you might be able to literally just call functions by writing them in with the bot so :D
    definitely attempt to use transpose and sort functions in order to

    you would probably have to find out how to do letter iteration first

    after that, you would probably transpose all of the data onto sorted rankings and then use sort functions
    that will sort by median and average"""
    def sort_ranking(self) -> None:
        print("")