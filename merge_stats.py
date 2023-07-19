import pandas as pd
import numpy as np
import argparse
import os

from copy import deepcopy


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    # parser.add_argument('race', type = str)
    parser.add_argument('race_length', type = str)
    parser.add_argument('gender', type = str)
    parser.add_argument("--age_group", nargs="*", type=float, default=[25, 26, 27, 28, 29])
    args = parser.parse_args()


    # Get all files into one dataframe
    files = ["./stats/" + i for i in os.listdir("./stats/")]
    print(files)

    c = 0
    for file in files:
        if c == 0:
            df = pd.read_csv(file)
        else:
            cur = pd.read_csv(file)
            # df = df.append(cur)
            df = pd.concat([df, cur])
        c += 1



    df.columns = ["Event", "Date", "Race Length", 'Score', "Time", "FN", "LN"]
    df = df.dropna(how = "any")

    df.to_csv("./here.csv", index = False)

    # df["year"] = df["Date"].str.split(" ").str[-1]
    df["year"] = df["Event"].str[0:5].str.strip()
    df["Race"] = None
    df["Race"] = np.where(df.Event.str.contains("Intermediate"), "Olympic", df.Race)
    df["Race"] = np.where(df.Event.str.contains("Short"), "Sprint", df.Race)
    df["Race"] = np.where(df.Event.str.contains("Olympic"), "Olympic", df.Race)
    df["Race"] = np.where(df.Event.str.contains("Sprint"), "Sprint", df.Race)
    df["Race"] = np.where(df.Event.str.contains("Long"), "Half Iron", df.Race)
    df["Race"] = np.where(df.Event.str.contains("Ironman"), "Half Iron", df.Race)
    df["Score"] = pd.to_numeric(df["Score"], errors='coerce')
    df["Name"] = df["FN"] + " " + df["LN"]
    df = df.dropna()

    p_stats_raw = deepcopy(df)
    p_avg_scores_allraces = deepcopy(df)
    p_avg_scores_allraces = pd.DataFrame(p_avg_scores_allraces.groupby(["Name"])["Score"].mean()).reset_index()
    p_avg_scores_allraces = p_avg_scores_allraces.sort_values(by = "Score", ascending = False)


    recent_olympic = deepcopy(df)
    recent_olympic = recent_olympic[recent_olympic["Race"] == args.race_length]
    recent_olympic = recent_olympic[recent_olympic["year"].isin(['2022', '2023'])]
    recent_olympic["Time"] = recent_olympic["Time"].str.split(".").str[0]
    # recent_olympic["Time"] = pd.to_timedelta(cleanDF['Running-Time'
    recent_olympic["Time"] = pd.to_datetime(recent_olympic['Time'], infer_datetime_format = True)
    recent_olympic = recent_olympic.groupby('Name').aggregate({'Score':'mean','Time':'mean'}).reset_index()
    recent_olympic = recent_olympic.sort_values(by = "Score", ascending = False)
    recent_olympic["Time"] = recent_olympic["Time"].astype(str).str.split(" ").str[1].str.split(".").str[0]

    racers = pd.read_csv("./participants.csv")
    racers = racers.drop_duplicates(subset = "Name")
    racers["Name"] = racers["Name"].str.split(" ").str[0:2].str.join(" ")

    age_group_male = deepcopy(df)
    age_group_male = pd.merge(age_group_male, racers, on = "Name")
    age_group_male['Time'] = age_group_male['Time'].str.split(".").str[0]
    age_group_male['Time'] = pd.to_timedelta(age_group_male.Time)
    age_group_male["Age"] = age_group_male["Age"].astype(int)
    age_group_male = age_group_male[age_group_male["Age"].isin(args.age_group)]
    age_group_male = age_group_male[age_group_male["Gender"] == args.gender]
    age_group_male = age_group_male[age_group_male["Race"] == args.race_length]

    if len(age_group_male) != 0:
        # age_group_male = pd.DataFrame(age_group_male.groupby(["Name"])["Score", "Time"].mean()).reset_index()
        age_group_male = age_group_male.groupby('Name').aggregate({'Score':'mean','Time':'mean'}).reset_index()
        age_group_male = age_group_male.sort_values(by = "Score", ascending = False)
        age_group_male["Time"] = age_group_male["Time"].astype(str).str.split(" ").str[2].str.split(".").str[0]

    # age_group_male.to_csv(f"./participant_stats_{args.race_length}.csv", index = False)

    with pd.ExcelWriter('output.xlsx') as writer:  # doctest: +SKIP
        p_stats_raw.to_excel(writer, sheet_name='p_stats_raw')
        p_avg_scores_allraces.to_excel(writer, sheet_name='p_avg_scores_allraces')
        recent_olympic.to_excel(writer, sheet_name=f'recent_{args.race_length.lower()}')
        age_group_male.to_excel(writer, sheet_name=f'age_group_{args.gender.lower()}')

