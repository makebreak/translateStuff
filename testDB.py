import os
import file 
import csv
import config
import dataset

# translate function
def translateFunc(text):
    translation = translate_client.translate(
        text,
        source_language=source,
        target_language=target)
    print(u'Translation: {}'.format(translation['translatedText']))
    translatedText = (format(translation['translatedText']))
    return translatedText 

# in file db
ORIGINAL_FILE = str(config.THIS_DIR / "in.db")

# db to write to
TRANSLATED_FILE = str(config.THIS_DIR / "out.db")

# Connect to original db with scraped data 
dbApps = dataset.connect('sqlite:///{}'.format(ORIGINAL_FILE))
appTable = dbApps['android_apps']

# Connect to db where we store translations
db = dataset.connect('sqlite:///{}'.format(TRANSLATED_FILE))
# table
tab = db['translated']

# Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = file.dirname

# Imports the Google Cloud client library
from google.cloud import translate

# Instantiates a client
translate_client = translate.Client()

# The target and source languages
source= 'ru'
target = 'en'

# translate each entry and write to a db
result = dbApps.query('SELECT title, summary FROM android_apps WHERE LANG=\''+source + '\'')
#for app in appTable:
for row in result:
    titleText = row['title']
    print(titleText)
    summaryText=row['summary']

    # translate text - call function
    translatedTitleText = translateFunc(titleText)
    print("translated Title text: " + translatedTitleText)
    
    #insert into new db's translation table
    #    tab.insert(dict(text1=titleText, text2=translatedText))

