# tri-scraper


## Files

- get_athletes.py: scrapes a runsignup page for all of the athletes registered for the race
- get_stats.py: opens an automated chrome browser page (don't close this!) that iterates over the particpants.csv file that get_athletes.py produces. Each participant is searched in the USA Tri database and their stats are downloaded as CSV's into a folder labeled *stats*
- merge_stats.py: merges everyone's stats into an excel file labeled *output.xlsx*


## How to run
1. Create a new conda environment using the requirements.txt file by running:  
``` conda create --name scrape --file requirements.txt ```
2. Activate the new environment with:  
``` conda activate scrape ```
3. Give excecution permission to the shell file ```scrape.sh``` by running   
```chmod +x scrape.sh```  
in your terminal
4. Replace arguments in the ```scrape.sh``` file (descriptions below).
5. Run the ```scrape.sh``` file by running  
 ```./scrape.sh```  
 in your terminal.


## ```scrape.sh``` Argument Descriptions
- GENDER: One of [Female, Male]
- RACELENGTH: One of [Sprint, Olympic, Half Iron]
- LINK: The link to the RunSignup page (ex: https://runsignup.com/Race/FindARunner/?raceId=13356&embedId2=mQezHpIT)
- race name: Found in the ```python3 get_stats.py``` call (there is no argument name, sorry). Get this from the RunSignup table for the race you are doing in the 'Event' column.
- age_group (found in line 16 of scrape.sh file in the ```python3 merge_stats.py``` call): each age in the age group (separated by spaces)


## What happens after you run ```scrape.sh```
- It'll run through get_athletes.py -> get_stats.py -> merge_stats.py in that order.
- You won't need to do anything while it's running.
- When the get_stats.py starts running, a Chrome browser window will open and the program will start styping things in and clicking buttons. Don't close this window! You can do other work on your computer while its running, just don't close it (:
- It's done after *output.xlsx* is written. The automated chrome window should close automatically after get_stats is done, but if it doesn't, you can close it when the program is done.