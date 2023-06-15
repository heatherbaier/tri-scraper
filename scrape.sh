#!/bin/bash

mkdir stats
mkdir stats_m

GENDER="Female"
RACELENGTH="Sprint"

echo "RunSignUp Link: $1."
echo "Race: $2."
echo "Gender: $GENDER."
echo "Race Length: $RACELENGTH"

python3 get_athletes.py $1
python3 get_stats.py "Culpeper Sprint Triathlon (Individual)" $RACELENGTH
python3 merge_stats.py $RACELENGTH $GENDER --age_group 25 26 27 28 29
