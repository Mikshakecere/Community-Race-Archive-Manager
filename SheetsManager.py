import multiprocessing
import time
class SheetsManager:
    def __init__(self, sheets, ssid):
        self.sheets = sheets
        self.ssid = ssid

    def lb_to_t3(self) -> None:
        """

        :return:
        """
        print("Checking for newer data...")
        start = time.time()
        latest = self.sheets.values().get(spreadsheetId=self.ssid,
                                          range=f"Top 3!B4").execute().get("values")[0][0]
        latest = int(latest[20:])+1
        row = 2*(latest-1)+8
        try:
            self.sheets.values().get(spreadsheetId=self.ssid,
                                     range=f"Leaderboard!K{row}").execute().get("values")[0][0]
        except TypeError:
            print("Row",str(latest),"\nThere is no new data to be processed. Terminating lb_to_t3 method")
            return None
        print("Creating dictionary and processing leaderboard data...", end=" ")
        places = {
            "placed0": {},
            "placed1": {},
            "placed2": {}
        }
        end = time.time()
        print("Prep runtime:", (end - start) * 10 ** 3, "ms")

        start = time.time()
        print("Looping through columns...", end=" ")
        if latest != 1:
            for i in range(3):
                place = self.sheets.values().batchGet(spreadsheetId=self.ssid,
                                                      ranges=[f"Top 3!{chr(66+(i*3))}10:{chr(66+(i*3))}",f"Top 3!{chr(68+(i*3))}10:{chr(68+(i*3))}"],
                                                      majorDimension="COLUMNS").execute().get("valueRanges")
                places[f"placed{i}"] = self.lists_to_dict(place[0].get("values")[0],place[1].get("values")[0])
        row = 2*(latest-1)+8
        while (True):
            try:
                value = self.sheets.values().batchGet(spreadsheetId=self.ssid,
                                                      ranges=[f"Leaderboard!K{row}", f"Leaderboard!M{row}", f"Leaderboard!O{row}"]).execute().get("valueRanges")
                values = []
                for i in range(3):
                    values.append(value[i].get("values")[0][0])
            except TypeError:
                latest = self.sheets.values().get(spreadsheetId=self.ssid,
                                                  range=f"Leaderboard!B{row-2}").execute().get("values")[0][0]
                break
            places = self.dict_update(values, places)
            row += 2
        end = time.time()
        print("Collection runtime:", (end - start) * 10 ** 3, "ms")

        start = time.time()
        print("Sorting dictionary...", end=" ")
        for place in places:
            places[place] = dict(sorted(places[place].items(), key=lambda x:x[1], reverse=True))
        end = time.time()
        print("Sorter runtime:", (end - start) * 10 ** 3, "ms")

        start = time.time()
        print("Updating total Top 3...", end=" ")
        processes = []
        for i in range(3):
            process = multiprocessing.Process(target=self.top_3_updater,args=(places[f"placed{i}"],66+(i*3)))
            process.start()
            processes.append(process)
        self.sheets.values().update(spreadsheetId=self.ssid, range=f"Top 3!B4", valueInputOption="USER_ENTERED",
                                    body={"values": [[f"Last Updated: Race #{latest}"]]}).execute()
        end = time.time()
        print("Updater runtime:", (end - start) * 10 ** 3, "ms")

    def lists_to_dict(self, list1, list2) -> dict:
        list2 = [eval(i) for i in list2]
        return {list1[i]: list2[i] for i in range(len(list1))}

    def dict_update(self, values, places) -> dict:
        """
        dict_update does this

        :param values: values is a list of values
        :param places: places is a list of places
        :return: dictionary places
        """
        for i in range(3):
            if values[i] == "N/A":
                pass
            elif values[i] not in places[f"placed{i}"]:
                places[f"placed{i}"][values[i]] = 1
            else:
                places[f"placed{i}"][values[i]] += 1
        return places

    def top_3_updater(self, place, col) -> None:
        """
        top_3_updater will update the sheet "Top 3" with the new information in the dictionary 'places'

        honestly i could try and modify the update function to check if a name is already there and if it is just add
        but i dont think that could scale very well anyway and its fine

        :param place: dictionary of dictionaries to have information accessed and used to update the sheet "Top 3"
        :param col: value that remains unchanged in order to be able to move on to the next column
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


    def row_add(self, count, starting_row, ending_row) -> None:
        """
        row_add

        :param starting_row:
        :param ending_row:
        :return:
        """

        while starting_row < ending_row:
            self.sheets.values().update(spreadsheetId=self.ssid,
                                        range=f"Leaderboard!B{starting_row}",
                                        valueInputOption="USER_ENTERED",
                                        body={"values": [[f"{count}"]]}).execute()
            starting_row += 2
            count += 1

    def reset_t3(self) -> None:
        print("")

    """check where the last race name before none type is and then take both name and race num
    go to the race ranking sheet and see where the race needs to be updated to
    only take races from last updated on race ranking to last updated on race lb
    f"Race #{race_number}: \"{race_name}\" by {race_creator}"""
    def lb_to_ranking(self) -> None:
        print("")

    """
    after that, you would probably transpose all of the data onto sorted rankings and then use sort functions
    that will sort by median and average
    ok im 99% sure the google sort function is absolutely fucking useless for me thanks
    """
    def sort_ranking(self) -> None:
        print("")

    def auto_format(self, num, col) -> None:
        raceTitle = "balls"
        raceHost = "balls"
        print(f"Race #{num}: \"{raceTitle}\" by {raceHost}")