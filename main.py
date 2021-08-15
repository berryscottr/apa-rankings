import pandas as pd
from sklearn.linear_model import LinearRegression


def predict(independent_vars, dependent_var):
    regression_model = LinearRegression()
    model = regression_model.fit(independent_vars, dependent_var)
    predictors = pd.concat([dependent_var, independent_vars.iloc[:, 1:]], axis=1)
    prediction = regression_model.predict(predictors)
    r_squared = 1 - (float(sum((dependent_var-prediction)**2)))/sum((dependent_var-pd.Series.mean(dependent_var))**2)
    adj_r_squared = 1 - (1-r_squared)*(len(dependent_var)-1)/(len(dependent_var)-independent_vars.shape[1]-1)
    if len(independent_vars.columns) == 2:
        print("{} = {:.2f} + {:.2f} * {} + {:.2f} * {}".format(
            dependent_var.name, regression_model.intercept_, regression_model.coef_[0], independent_vars.columns[0],
            regression_model.coef_[1], independent_vars.columns[1]))
    elif len(independent_vars.columns) == 3:
        print("{} = {:.2f} + {:.2f} * {} + {:.2f} * {} + {:.2f} * {}".format(
            dependent_var.name, regression_model.intercept_, regression_model.coef_[0], independent_vars.columns[0],
            regression_model.coef_[1], independent_vars.columns[1], regression_model.coef_[2],
            independent_vars.columns[2]))
    if abs(max(r_squared, adj_r_squared)) <= 1:
        print("{} model explains {:.2f}% of the match results".format(
            dependent_var.name, max(r_squared, adj_r_squared) * 100))
    else:
        print("{} model is crap. As an underpost, results cannot be predicted. They are too dependent on the "
              "table-controlling opponent".format(dependent_var.name))
    return model, prediction, adj_r_squared


def build_table(data, preds):
    column_list = []
    for opp_skill in range(2, 8):
        column = []
        team_skill = data["Skill_Level"].values
        for index, skill in enumerate(team_skill):
            if abs(skill - opp_skill) >= 2:
                column.append("")
            elif skill > opp_skill:
                column.append(preds["Over PPM"].values[index])
            elif skill == opp_skill:
                column.append(preds["Equal PPM"].values[index])
            elif skill < opp_skill:
                column.append(preds["Under PPM"].values[index])
        column = pd.DataFrame(column, columns=[opp_skill], index=data.index.values)
        column_list.append(column)
    table = pd.concat(column_list, axis=1)
    return table


def main():
    player_data = pd.read_csv("data/playerData.csv", index_col=0, na_values='?').astype(float)
    player_data = player_data.fillna(pd.Series.mean(player_data))
    prediction = pd.DataFrame(predict(
        player_data[["Last_Season_PPM", "Career_Win_Chance"]], player_data["PPM"])[1], columns=["Pred PPM"],
                              index=player_data.index.values)
    overpost_prediction = pd.DataFrame(predict(
        player_data[["Last_Season_PPM_Overpost", "Last_Season_PPM", "Career_Win_Chance"]],
        player_data["PPM_Overpost"])[1], columns=["Over PPM"], index=player_data.index.values)
    equalpost_prediction = pd.DataFrame(predict(
        player_data[["Last_Season_PPM_Equalpost", "Last_Season_PPM", "Career_Win_Chance"]],
        player_data["PPM_Equalpost"])[1], columns=["Equal PPM"], index=player_data.index.values)
    # underpost_prediction = pd.DataFrame(predict(
    #     player_data[["Last_Season_PPM_Underpost", "Last_Season_PPM", "Career_Win_Chance"]],
    #     player_data["PPM_Underpost"])[1], columns=["Under PPM"], index=player_data.index.values)
    print("PPM underpost derived from overpost, equalpost, and overall. This is necessary because as an underpost, "
          "results cannot be predicted using our own player's data. "
          "They are too dependent on the table-controlling opponent")
    underpost_prediction = pd.DataFrame(
        prediction.values * 3 - overpost_prediction.values - equalpost_prediction.values, columns=["Under PPM"],
        index=player_data.index.values)
    predictions = pd.DataFrame(pd.concat(
        [prediction, overpost_prediction, equalpost_prediction, underpost_prediction],
        axis=1)).round(2).abs()
    predictions.to_csv("data/predictions.csv")
    expected_ppm = build_table(player_data, predictions)
    # normalize e_ppm
    for index, row in expected_ppm.iterrows():
        for item in row.iteritems():
            if item[1] != '':
                if item[1] > 3:
                    expected_ppm[item[0]][index] = 3 - (item[1] - 3)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print("Expected PPM vs Opponent Skill Level\n", expected_ppm)
    expected_ppm.to_csv("data/expected_ppm.csv")


if __name__ == '__main__':
    main()
