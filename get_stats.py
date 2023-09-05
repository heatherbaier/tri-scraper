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
    txt = [i for i in txt if not i.endswith("3rd")]
    txt = [i for i in txt if not i.endswith("2nd")]
    txt = [i for i in txt if not i.endswith("2th")]
    txt = [i for i in txt if not i.endswith("1th")]
    txt = [i for i in txt if not i.endswith("1st")]
    txt = [i for i in txt if not i.endswith("3th")]
    txt = [i for i in txt if not i.endswith("4th")]
    txt = [i for i in txt if not i.endswith("5th")]
    txt = [i for i in txt if not i.endswith("6th")]
    txt = [i for i in txt if not i.endswith("7th")]
    txt = [i for i in txt if not i.endswith("8th")]
    txt = [i for i in txt if not i.endswith("9th")]
    txt = [i for i in txt if not i.endswith("0th")]
    chunks = [txt[x:x+5] for x in range(0, len(txt), 5)]

    df = pd.DataFrame(chunks)
    df["first_name"] = fn
    df["last_name"] = ln

    print(df)

    df.to_csv(f"./stats/{ln}_{fn}_stats.csv", index = False)

    time.sleep(2)


if __name__ == "__main__":
    
    nats = 0
    
    parser = argparse.ArgumentParser()
    if nats == 0:
        parser.add_argument('race', type = str)
        parser.add_argument('race_length', type = str)
        parser.add_argument('gender', type = str)
    args = parser.parse_args()

    if nats == 0:
        print(args.race)
    
        people = pd.read_csv("./participants.csv")
        people = people[people["Event"] == args.race]
        people = people.drop_duplicates(subset = ["Name"])
        people.to_csv(f"./{args.race_length}_participants.csv", index = False)
    else:
        people = pd.read_csv("usa_nats.csv")
        people["Name"] = people["Attendee First Name"].str.title() + " " + people["Attendee Last Name"].str.title() + "  More Details"
        people = people.rename(columns = {"Age as of 12/31/2023": "Age"})
        print(people.shape)
        people = people[people["Ticket Type"].str.contains("Olympic")]
        print(people.head())
        print(people.shape)

        people.to_csv('./participants.csv')

    driver = webdriver.Chrome()#executable_path = "/Users/heatherbaier/Desktop/tri_scrape/tri_scrape/chromedriver")

    url = "https://rankings.usatriathlon.org/RaceResult/AthleteResults"
    
    stateName = ["Alabama","Kentucky","Ohio","Alaska","Louisiana","Oklahoma","Arizona",\
        "Maine","Oregon","Arkansas","Maryland","Pennsylvania","American Samoa","Massachusetts",\
        "Puerto Rico","California","Michigan","Rhode Island","Colorado","Minnesota",\
        "South Carolina","Connecticut","Mississippi","South Dakota","Delaware","Missouri",\
        "Tennessee","District of Columbia","Montana","Texas","Florida","Nebraska","Trust Territories",\
        "Georgia","Nevada","Utah","Guam","New Hampshire","Vermont","Hawaii","New Jersey",\
        "Virginia","Idaho","New Mexico","Virgin Islands","Illinois","New York","Washington",\
        "Indiana","North Carolina","West Virginia","Iowa","North Dakota","Wisconsin",\
        "Kansas","Northern Mariana Islands","Wyoming"]
    stateAbv =["AL","KY","OH","AK","LA","OK","AZ","ME","OR","AR","MD","PA","AS","MA",\
    "PR","CA","MI","RI","CO","MN","SC","CT","MS","SD","DE","MO","TN","DC","MT","TX",\
    "FL","NE","TT","GA","NV","UT","GU","NH","VT","HI","NJ","VA","ID","NM","VI","IL",\
    "NY","WA","IN","NC","WV","IA","ND","WI","KS","MP","WY"]

    for col, row in people.iterrows():

        fn = row.Name.split(" ")[0]
        ln = row.Name.split(" ")[1]
        print(fn, ln)
        pg = 1
        res = 0
        verified = 0
        while res == 0:
            url = f"https://member.usatriathlon.org/results/athletes?last_name={ln}&page={pg}" #url of just last name

            driver.get(url)

            time.sleep(2)

            txt = driver.find_element(By.XPATH, "/html/body").text
            txt = txt.splitlines()
            txt = [i.strip() for i in txt]
            txt = [i.title() for i in txt]
            print(txt)
            name = ", ".join([ln, fn])
            print(name)

            #c = txt.count(name)
            c = 0
            for i in range(len(txt)):
                siz = min(len(txt[i]),len(name))
                if txt[i][0:siz]==name[0:siz]: #fixes issue of shorten name (chris vs christopher) by searching for only like characters
                    if txt[i+2][2:5] == 'Yrs': #normally where age is on rankings
                        age = int(txt[i+2][0:2])
                    elif txt[i+1][2:5] == 'Yrs': #where age is when no location is present
                        age = int(txt[i+1][0:2])
                    else:
                        age = 0
                    if abs(age - int(row.Age)) < 2: #age +- 1 year range
                      ind = txt[i].index(',')
                      ln = txt[i][0:ind] #grab last name rankings has (as opposed to last name from registration)
                      fn = txt[i][ind+2:] #similar for first name
                      if ',' in txt[i+1]: #if comma then split city, state pair
                          state = txt[i+1][txt[i+1].index(',')+2:]
                          city = txt[i+1][0:txt[i+1].index(',')]
                      else: #if no comma assume state (not an issue if it is a city, just won't verify)
                          state = txt[i+1]
                          city = ''
                      stateVer = row.State[0:2] #state from registration
                      if stateVer in stateAbv: #make sure state is a state
                          stateVer = stateName[stateAbv.index(stateVer)] #change state from name to abreviation
                          if state == stateVer:
                              verified = 1 #select by location later
                              location = txt[i+1] #grab name of location that rankings has
                              res = 1 #stop looking through the names
                              break
                elif txt[i][0:13] == 'Showing To Of': #this should be when all names have been searched through rankings (no location verification)
                    res = 1
                    break
            pg+=1

        
        url = f"https://member.usatriathlon.org/results/athletes?first_name={fn}&last_name={ln}" #now do both first and last name

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

        # Case 1: Only one person with name
        if c == 1:
            if verified == 1: #choose by location, not name
                try:
                    
                    l = driver.find_element(By.XPATH, f"//div[normalize-space()='{str(location)}']")#.text
                    l.click()

                    time.sleep(2)

                    txt = driver.find_element(By.XPATH, "/html/body").text
                    txt = txt.splitlines()
                    txt = [i.strip() for i in txt]

                    stats_to_table(txt, fn, ln)
                    
                except: #try case issues (not all resolvable such as Lake in the Hills, IL)
                    
                    try:
                        
                        location = city.upper() + ", " + state
                        l = driver.find_element(By.XPATH, f"//div[normalize-space()='{str(location)}']")#.text
                        l.click()

                        time.sleep(2)

                        txt = driver.find_element(By.XPATH, "/html/body").text
                        txt = txt.splitlines()
                        txt = [i.strip() for i in txt]

                        stats_to_table(txt, fn, ln)
                        
                    except:
                    
                        try:
                            
                            location = city.lower() + ", " + state
                            l = driver.find_element(By.XPATH, f"//div[normalize-space()='{str(location)}']")#.text
                            l.click()

                            time.sleep(2)

                            txt = driver.find_element(By.XPATH, "/html/body").text
                            txt = txt.splitlines()
                            txt = [i.strip() for i in txt]

                            stats_to_table(txt, fn, ln)
                            
                        except:
                        
                            verified = 0
                        
            if verified == 0: #not verified so go by name
                try:

                    l = driver.find_element(By.XPATH, f"//*[text()='{str(fn)}']")#.text #first name avoids casing issues in last name (something like DeVincenzo)
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
                        l = driver.find_element(By.XPATH, f"//*[text()='{str(fn.upper())}']")#.text
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
            if verified == 1:
                
                try:
                    
                    l = driver.find_element(By.XPATH, f"//div[normalize-space()='{str(location)}']")#.text
                    l.click()

                    time.sleep(2)

                    txt = driver.find_element(By.XPATH, "/html/body").text
                    txt = txt.splitlines()
                    txt = [i.strip() for i in txt]

                    stats_to_table(txt, fn, ln)
                    
                except:
                    
                    try:
                        
                        location = city.upper() + ", " + state
                        l = driver.find_element(By.XPATH, f"//div[normalize-space()='{str(location)}']")#.text
                        l.click()

                        time.sleep(2)

                        txt = driver.find_element(By.XPATH, "/html/body").text
                        txt = txt.splitlines()
                        txt = [i.strip() for i in txt]

                        stats_to_table(txt, fn, ln)
                        
                    except:
                    
                        try:
                            
                            location = city.lower() + ", " + state
                            l = driver.find_element(By.XPATH, f"//div[normalize-space()='{str(location)}']")#.text
                            l.click()

                            time.sleep(2)

                            txt = driver.find_element(By.XPATH, "/html/body").text
                            txt = txt.splitlines()
                            txt = [i.strip() for i in txt]

                            stats_to_table(txt, fn, ln)
                            
                        except:
                        
                            verified = 0
            if verified==0:
                for i in [age, age - 1, age + 1]:

                    print("AGE: ", i)

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
