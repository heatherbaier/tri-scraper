#!/bin/bash

mkdir stats
mkdir stats_m

GENDER="Male"
RACELENGTH="Olympic"
LINK="https://runsignup.com/Race/FindARunner/?raceId=13356&embedId2=mQezHpIT"

echo "RunSignUp Link: $LINK."
echo "Gender: $GENDER."
echo "Race Length: $RACELENGTH"

python3 get_athletes.py $LINK
python3 get_stats.py "Patriots Olympic Triathlon (Individual)" $RACELENGTH $GENDER
python3 merge_stats.py $RACELENGTH $GENDER --age_group 25 26 27 28 29



