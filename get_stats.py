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

from states import *


def find_indices(list_to_check, item_to_find):
    indices = []
    for idx, value in enumerate(list_to_check):
        if value == item_to_find:
            indices.append(idx)
    return indices


def stats_to_table(txt, fn, ln):

    score_index = txt.index("Youth") + 1
    last_index = txt.index("+")

    txt = txt[score_index:last_index]
    txt = [i for i in txt if not i.endswith("th")]
    txt = [i for i in txt if not i.endswith("rd")]
    txt = [i for i in txt if not i.endswith("2nd")]
    txt = [i for i in txt if not i.endswith("st")]
    chunks = [txt[x:x+5] for x in range(0, len(txt), 5)]

    df = pd.DataFrame(chunks)
    df["first_name"] = fn
    df["last_name"] = ln

    print(df)

    df.to_csv(f"./stats/{ln}_{fn}_stats.csv", index = False)

    time.sleep(2)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    # parser.add_argument('race', type = str)
    # parser.add_argument('race_length', type = str)
    # parser.add_argument('gender', type = str)
    args = parser.parse_args()

    # print(args.race)
    
    # people = pd.read_csv("./participants.csv")
    # people = people[people["Event"] == args.race]
    # people = people.drop_duplicates(subset = ["Name"])
    # people.to_csv(f"./{args.race_length}_participants.csv", index = False)

    people = pd.read_csv("usa_nats.csv")[0:50]
    people["Name"] = people["Attendee First Name"].str.title() + " " + people["Attendee Last Name"].str.title() + "  More Details"
    people = people.rename(columns = {"Age as of 12/31/2023": "Age"})
    print(people.head())    
    print(people.shape)

    people.to_csv('./participants.csv')

    driver = webdriver.Chrome()#executable_path = "/Users/heatherbaier/Desktop/tri_scrape/tri_scrape/chromedriver")

    url = "https://rankings.usatriathlon.org/RaceResult/AthleteResults"

    for col, row in people.iterrows():

        fn = row.Name.split(" ")[0]
        ln = row.Name.split(" ")[1]
        print(fn, ln)

        url = f"https://member.usatriathlon.org/results/athletes?first_name={fn}&last_name={ln}"

        driver.get(url)

        time.sleep(2)

        with open("./record.txt", "a") as f:
            f.write("\n" + fn + " " + ln + " ")

        txt = driver.find_element(By.XPATH, "/html/body").text
        txt = txt.splitlines()
        txt = [i.strip() for i in txt] 
        txt = [i.title() for i in txt]

        name = ", ".join([ln, fn])
        print(name)

        c = txt.count(name)

        print("COUNT: ", c)

        if name not in txt:
            continue
        else:
            res = 1

        # Case 2: Only one person with name
        if c == 1:

            try:

                l = driver.find_element(By.XPATH, f"//*[text()='{str(ln)}']")#.text
                l.click()    

                time.sleep(2)

                txt = driver.find_element(By.XPATH, "/html/body").text
                txt = txt.splitlines()   
                txt = [i.strip() for i in txt] 

                print(txt, "\n\n")

                stats_to_table(txt, fn, ln)

            except:

                try:

                    # MIGHT HAVE FAILED BECAUSE OF GOSH DARN HECKIN CASING SO TRY AGAIN WITH ALL CAPS
                    l = driver.find_element(By.XPATH, f"//*[text()='{str(ln.upper())}']")#.text
                    l.click()    

                    time.sleep(2)

                    txt = driver.find_element(By.XPATH, "/html/body").text
                    txt = txt.splitlines()   
                    txt = [i.strip() for i in txt] 

                    print(txt, "\n\n")

                    stats_to_table(txt, fn, ln)

                # lol u suck
                except:
                    
                    pass

        # Case 2: Multiple people with name
        elif c > 1:

            age = int(row.Age)
            fail = 1
            for i in [age, age - 1, age + 1]:

                print("AGE: ", age)

                try:

                    l = driver.find_element(By.XPATH, f"//*[text()='{str(i)}yrs']")#.text
                    l.click()   

                    time.sleep(2)

                    txt = driver.find_element(By.XPATH, "/html/body").text
                    txt = txt.splitlines()   
                    txt = [i.strip() for i in txt] 

                    stats_to_table(txt, fn, ln)

                    fail = 0

                except:

                    fail = 1
            
                if fail == 0:

                    continue
