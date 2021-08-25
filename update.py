import json
import pandas as pd
from shutil import copyfile

pd.options.mode.chained_assignment = None


class PlayerData:
    def __init__(self, file):
        self.filename = file
        self.entries = []
        self.data = self.read()
        self.json_data = []

    def read(self):
        with open(self.filename) as data_file:
            data = json.load(data_file)
        player_data = pd.json_normalize(data).set_index("Player Name")
        data_file.close()
        return player_data

    def write(self):
        copyfile(self.filename, self.filename+".bak")
        json_text = json.dumps(str(self.json_data).replace("\'", "\"", -1), indent=4)
        with open(self.filename, "w") as jsonFile:
            jsonFile.write(json_text)
        jsonFile.close()

    def enter_data(self):
        num_matches = eval(input("Number of games? "))
        session = input("Which Session? ")
        while len(self.entries) < num_matches:
            player = input("Player name? ")
            over_under = input("Overpost, equalpost, or underpost? (o/e/u) ").lower()
            points = eval(input("Points scored? "))
            self.entries.append([session, player, over_under, points])

    def update_data(self):
        for game in self.entries:
            career_wins = self.data["Career Win Chance"][game[1]] * self.data["Career Games Played"][game[1]]
            self.data["Career Games Played"][game[1]] += 1
            if game[3] >= 2:
                career_wins += 1
            self.data["Career Win Chance"][game[1]] = career_wins / self.data["Career Games Played"][game[1]]
            self.data["Session.{}.PPM".format(game[0])][game[1]].append(game[3])
            if game[2] == "o":
                self.data["Session.{}.PPM Overpost".format(game[0])][game[1]].append(game[3])
            elif game[2] == "e":
                self.data["Session.{}.PPM Equalpost".format(game[0])][game[1]].append(game[3])
            elif game[2] == "u":
                self.data["Session.{}.PPM Underpost".format(game[0])][game[1]].append(game[3])
        for player in self.data.index.values:
            self.json_data.append({
                "Player Name": player,
                "Skill Level": self.data["Skill Level"][player],
                "Career Win Chance": round(self.data["Career Win Chance"][player], 4),
                "Career Games Played": self.data["Career Games Played"][player],
                "Session": {
                    "Spring 2021": {
                        "PPM": self.data["Session.Spring 2021.PPM"][player],
                        "PPM Overpost": self.data["Session.Spring 2021.PPM Overpost"][player],
                        "PPM Equalpost": self.data["Session.Spring 2021.PPM Equalpost"][player],
                        "PPM Underpost": self.data["Session.Spring 2021.PPM Underpost"][player]
                    },
                    "Summer 2021": {
                        "PPM": self.data["Session.Summer 2021.PPM"][player],
                        "PPM Overpost": self.data["Session.Summer 2021.PPM Overpost"][player],
                        "PPM Equalpost": self.data["Session.Summer 2021.PPM Equalpost"][player],
                        "PPM Underpost": self.data["Session.Summer 2021.PPM Underpost"][player]
                    },
                    "Fall 2021": {
                        "PPM": self.data["Session.Fall 2021.PPM"][player],
                        "PPM Overpost": self.data["Session.Fall 2021.PPM Overpost"][player],
                        "PPM Equalpost": self.data["Session.Fall 2021.PPM Equalpost"][player],
                        "PPM Underpost": self.data["Session.Fall 2021.PPM Underpost"][player]
                    }
                }
            })


def main():
    player_data = PlayerData("data/playerData.json")
    player_data.enter_data()
    player_data.update_data()
    player_data.write()


if __name__ == '__main__':
    main()
