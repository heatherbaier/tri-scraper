import requests 

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

from bs4 import BeautifulSoup as bs 
import pandas as pd
import argparse

import time


def find_indices(list_to_check, item_to_find):
    indices = []
    for idx, value in enumerate(list_to_check):
        if value == item_to_find:
            indices.append(idx)
    return indices


def stats_to_table(txt):

    score_index = txt.index("Score") + 1
    last_index = txt.index([i for i in txt if "Corporate" in i][0])

    txt = txt[score_index:last_index]

    dnf = [i for i in txt if "DNF" in i]

    if len(dnf) != 0:
        indices = find_indices(txt, "DNF")
        for i in indices:
            print(indices)
            txt = txt[0:i - 2] + txt[i + 1:]

    chunks = [txt[x:x+4] for x in range(0, len(txt), 4)]

    df = pd.DataFrame(chunks)
    df["first_name"] = fn
    df["last_name"] = ln

    df.to_csv(f"./stats/{ln}_{fn}_stats.csv", index = False)

    time.sleep(2)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('race', type = str)
    parser.add_argument('race_length', type = str)
    parser.add_argument('gender', type = str)
    args = parser.parse_args()

    print(args.race)
    
    people = pd.read_csv("./participants.csv")
    people = people[people["Event"] == args.race]
    people = people.drop_duplicates(subset = ["Name"])
    people.to_csv(f"./{args.race_length}_participants.csv", index = False)

    print(people.shape)

    driver = webdriver.Chrome()#executable_path = "/Users/heatherbaier/Desktop/tri_scrape/tri_scrape/chromedriver")

    url = "https://rankings.usatriathlon.org/RaceResult/AthleteResults"

    for col, row in people.iterrows():

        url = "https://rankings.usatriathlon.org/RaceResult/AthleteResults"

        driver.get(url)

        fn = row.Name.split(" ")[0]
        ln = row.Name.split(" ")[1]
        print(fn, ln)

        # input = driver.find_element_by_id("FirstName")
        input = driver.find_element("id", "FirstName")
        input.send_keys(fn)

        input = driver.find_element("id", "LastName")
        input.send_keys(ln)

        time.sleep(2)

        input = driver.find_element("id", "btnSearchAthlete")
        input.click()

        time.sleep(5)

        with open("./record.txt", "a") as f:
            f.write("\n" + fn + " " + ln + " ")

        txt = driver.find_element(By.XPATH, "/html/body").text
        txt = txt.splitlines()

        # Case 1: No records available
        no_res = [i for i in txt if i == "No data to display"]

        with open("./record.txt", "a") as f:
            f.write("No res: " + str(len(no_res)) + " ")

        # Case 2: Only one person with name
        if len(no_res) == 0:

            multiple = [i for i in txt if i == "Choose Athlete"]

            with open("./record.txt", "a") as f:
                f.write("Multiple: " + str(len(multiple)) + " ")

            if len(multiple) == 0:

                try:

                    stats_to_table(txt)

                except:

                    with open("./record.txt", "a") as f:
                        f.write(" Failed! ")

            # Case 3: Multiple people with same name
            elif len(multiple) != 0:

                try:
                    
                    # click on the row with the matching age
                    age = row.Age
                    # l = driver.find_element_by_xpath(f"//*[text()='{str(age)}']") 
                    l = driver.find_element(By.XPATH, f"//*[text()='{str(age)}']")#.text
                    l.click()

                    time.sleep(2)

                    txt = driver.find_element(By.XPATH, "/html/body").text
                    txt = txt.splitlines()

                    stats_to_table(txt)

                except:

                    with open("./record.txt", "a") as f:
                        f.write(" Failed! ")