import random

import openpyxl
import pandas as pd


class Game:
    def __init__(self, player_name, player_skill_level, games_table, player_data, game_data):
        self.player_name = player_name
        self.player_skill_level = player_skill_level
        self.player_data = player_data
        self.game_data = game_data
        self.games_table = games_table
        self.player_points, self.opponent_points = self.wins2points()

    def wins2points(self):
        games_row = self.games_table.iloc[[self.player_skill_level]]
        opponent_skill_level = random.randint(2, 7)
        player_games_needed = int(list(games_row[opponent_skill_level].values.astype(str)[0])[0])
        opponent_games_needed = int(list(games_row[opponent_skill_level].values.astype(str)[0])[-1])
        player_wins = random.randint(0, player_games_needed)
        opponent_wins = random.randint(0, opponent_games_needed)
        if player_wins == player_games_needed:
            player_points = 2
            if opponent_wins == 0:
                player_points += 1
            opponent_points = 0
            if opponent_wins == opponent_games_needed - 1:
                opponent_points += 1
        else:
            opponent_points = 2
            if player_wins == 0:
                opponent_points += 1
            player_points = 0
            if player_wins == player_games_needed - 1:
                player_points += 1
        return player_points, opponent_points


def workbook2df(path, first_row_header, first_column_index):
    workbook = openpyxl.load_workbook(path).active
    rows = list(workbook.iter_rows(values_only=True))
    df = pd.DataFrame(rows)
    if first_row_header:
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header
    if first_column_index:
        df = df.set_index("SL")
    return df


def main():
    games_table = workbook2df("data/gamesToWin.xlsx", True, True)
    player_data = workbook2df("data/wookieMistakesPlayerData.xlsx", True, False)
    game_data = workbook2df("data/wookieMistakesSpring2022Games.xlsx", True, False)
    for index, row in player_data.iterrows():
        player_name = row["Name"]
        player_skill_level = row["Skill Level"]
        game = Game(player_name, player_skill_level, games_table, player_data, game_data)


if __name__ == '__main__':
    main()
