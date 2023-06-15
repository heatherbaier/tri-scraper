from bs4 import BeautifulSoup as bs 
import pandas as pd
import argparse



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type = str)
    args = parser.parse_args()

    print(args.url)

    # url = "https://runsignup.com/Race/FindARunner/?raceId=13356&embedId2=mQezHpIT"

    for i in range(0, 100):

        print("Page: ", i, end = "\r")

        try:

            if i == 0:
                url = args.url
                df = pd.read_html(url)[1]
            else:
                url = f"{args.url}&page={i}"   
                df = pd.concat([df, pd.read_html(url)[1]])

        except:

            break

    df.to_csv("./participants.csv", index = False)
