#!/bin/bash

# name file based on command line parameters
# Arguments: User lang1 country1 lang2 country2
old="$IFS"
IFS='_'
str="$*"
echo "$str"
IFS=$old

fname_prefix="/tmp/"$(date +"%Y%m%d")"_${str}"
echo $fname_prefix


# copy database
dst=${fname_prefix}_crawled_apps_translated.db
cp ~/appscraper/data/crawled_apps.db "${dst}"

# run updateDB.py on db to translate and update db
python3 updateDB.py $1 $2 android
python3 updateDB.py $1 $2 ios
python3 updateDB.py $3 $4 android
python3 updateDB.py $3 $4 ios

# run ml classifier on translated db, which creates a csv.gz file
cd ml && python3 create_phone_scanner_data.py ../phone_scanner/app-flags.csv

# save to cloud storage then delete
echo "Saving translated database as $dst"
rclone copy "$dst"  tdrive:TranslatedDatabases
rm "$dst"
