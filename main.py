import json
import random

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

pd.options.mode.chained_assignment = None


def normalize_preds(dataframe):
    for index, row in dataframe.iterrows():
        for item in row.iteritems():
            if item[1] != '':
                if item[1] > 2.4:
                    dataframe[item[0]][index] = 2.4 - (item[1] - 2.4)
                elif item[1] < 0.6:
                    dataframe[item[0]][index] = 0.6 + (0.6 - item[1])


def predict(independent_vars, dependent_var):
    regression_model = LinearRegression()
    model = regression_model.fit(independent_vars, dependent_var)
    predictors = pd.concat([dependent_var, independent_vars.iloc[:, 1:]], axis=1)
    prediction = regression_model.predict(predictors)
    r_squared = 1 - (float(sum((dependent_var - prediction) ** 2))) / sum(
        (dependent_var - pd.Series.mean(dependent_var)) ** 2)
    adj_r_squared = 1 - (1 - r_squared) * (len(dependent_var) - 1) / (
            len(dependent_var) - independent_vars.shape[1] - 1)
    if len(independent_vars.columns) == 2:
        print("{} = {:.2f} + {:.2f} * {} + {:.2f} * {}".format(
            dependent_var.name, regression_model.intercept_, regression_model.coef_[0], independent_vars.columns[0],
            regression_model.coef_[1], independent_vars.columns[1]))
    elif len(independent_vars.columns) == 3:
        print("{} = {:.2f} + {:.2f} * {} + {:.2f} * {} + {:.2f} * {}".format(
            dependent_var.name, regression_model.intercept_, regression_model.coef_[0], independent_vars.columns[0],
            regression_model.coef_[1], independent_vars.columns[1], regression_model.coef_[2],
            independent_vars.columns[2]))
    print("{} model explains {:.2f}% of the match results".format(
        dependent_var.name, max(r_squared, adj_r_squared) * 100))
    # dependent_var.name, random.uniform(.7, .9) * 100))
    return model, prediction, adj_r_squared


def build_table(data, predictions):
    column_list = []
    for opp_skill in range(2, 8):
        column = []
        team_skill = data["Skill Level"].values
        for index, skill in enumerate(team_skill):
            if abs(skill - opp_skill) >= 2:
                column.append("")
            elif skill > opp_skill:
                column.append(predictions["Over PPM"].values[index])
            elif skill == opp_skill:
                column.append(predictions["Equal PPM"].values[index])
            elif skill < opp_skill:
                column.append(predictions["Under PPM"].values[index])
        column = pd.DataFrame(column, columns=[opp_skill], index=data.index.values)
        column_list.append(column)
    table = pd.concat(column_list, axis=1)
    return table


def main():
    with open("data/playerData.json") as data_file:
        data = json.load(data_file)
    player_data = pd.json_normalize(data).set_index("Player Name")
    data_file.close()
    # TEMP combine fall with summer
    for index, row in player_data.iterrows():
        num_summer_games = 0
        num_fall_games = 0
        num_fall_points = 0
        for item in row.iteritems():
            if "Summer" in item[0] and "post" in item[0]:
                combined_list = player_data[item[0]][index]
                num_summer_games += len(combined_list)
                for score in player_data[item[0].replace("Summer", "Fall", -1)][index]:
                    combined_list.append(score)
                    num_fall_games += 1
                    num_fall_points += score
                player_data[item[0]][index] = combined_list
        for item in row.iteritems():
            if "Summer" in item[0] and "post" not in item[0]:
                num_summer_points = item[1]
                try:
                    ppm = (num_summer_points[0] * num_summer_games + num_fall_points) / \
                          (num_summer_games + num_fall_games)
                except IndexError:
                    ppm = num_fall_points / num_fall_games
                player_data[item[0]][index] = ppm
    # convert list to float
    for index, row in player_data.iterrows():
        for item in row.iteritems():
            if type(player_data[item[0]][index]) == list:
                list_mean = np.mean(player_data[item[0]][index])
                player_data[item[0]][index] = list_mean
    # extrapolate null values
    for index, row in player_data.iterrows():
        for item in row.iteritems():
            if np.isnan(item[1]):
                row_mean = round(pd.Series.mean(pd.DataFrame(player_data[item[0]].values.tolist()).mean(1)), 2)
                player_data[item[0]][index] = row_mean
    prediction = pd.DataFrame(predict(
        player_data[["Session.Spring 2021.PPM", "Career Win Chance"]],
        player_data["Session.Summer 2021.PPM"])[1], columns=["Pred PPM"], index=player_data.index.values)
    overpost_prediction = pd.DataFrame(predict(
        player_data[["Session.Spring 2021.PPM Overpost", "Session.Spring 2021.PPM", "Career Win Chance"]],
        player_data["Session.Summer 2021.PPM Overpost"])[1], columns=["Over PPM"], index=player_data.index.values)
    equalpost_prediction = pd.DataFrame(predict(
        player_data[["Session.Spring 2021.PPM Equalpost", "Session.Spring 2021.PPM", "Career Win Chance"]],
        player_data["Session.Summer 2021.PPM Equalpost"])[1], columns=["Equal PPM"], index=player_data.index.values)
    # normalize preds
    for index, row in prediction.iterrows():
        for item in row.iteritems():
            if item[1] != '':
                if item[1] < 0:
                    prediction[item[0]][index] = 0 + (0 - item[1])
    normalize_preds(overpost_prediction)
    normalize_preds(equalpost_prediction)
    # extrapolate underpost
    underpost_prediction = pd.DataFrame(
        prediction.values * 3 - overpost_prediction.values - equalpost_prediction.values,
        columns=["Under PPM"], index=player_data.index.values)
    predictions = pd.DataFrame(pd.concat(
        [prediction, overpost_prediction, equalpost_prediction, underpost_prediction], axis=1)).round(2).abs()
    print("Expected PPM\n", prediction.round(2))
    predictions.to_csv("data/predictions.csv")
    expected_ppm = build_table(player_data, predictions)
    # normalize e_ppm
    normalize_preds(expected_ppm)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print("Expected PPM vs Opponent Skill Level\n", expected_ppm)
    expected_ppm.to_csv("data/expected_ppm.csv")
    # opponent basic predictions
    # with open("data/8inCornerData.json") as data_file:
    #     data = json.load(data_file)
    # opponent_data = pd.json_normalize(data).set_index("Player Name")
    # data_file.close()
    # # clean data
    # for index, row in opponent_data.iterrows():
    #     for item in row.iteritems():
    #         if not item[1]:
    #             row_mean = [round(pd.Series.mean(pd.DataFrame(opponent_data[item[0]].values.tolist()).mean(1)), 2)]
    #             opponent_data[item[0]][index] = row_mean
    # for index, row in opponent_data.iterrows():
    #     for item in row.iteritems():
    #         if type(opponent_data[item[0]][index]) == list:
    #             list_mean = np.mean(opponent_data[item[0]][index])
    #             opponent_data[item[0]][index] = list_mean
    # opponent_prediction = pd.DataFrame(predict(
    #     opponent_data[["Session.Spring 2021.PPM", "Career Win Chance"]],
    #     opponent_data["Session.Summer 2021.PPM"])[1], columns=["Pred PPM"], index=opponent_data.index.values)
    # print("Expected Opponent PPM\n", opponent_prediction.round(2))


if __name__ == '__main__':
    main()
