import os
import file 
import csv
import config
import dataset

# in file 
ORIGINAL_FILE = str(config.THIS_DIR / "in.csv")

# db to write to
TRANSLATED_FILE = str(config.THIS_DIR / "out.db")

# Connect to db where we store translations
db = dataset.connect('sqlite:///{}'.format(TRANSLATED_FILE))
tab = db['translated']

# Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = file.dirname

# Imports the Google Cloud client library
from google.cloud import translate

# Instantiates a client
translate_client = translate.Client()

# The target language
source= 'ru'
target = 'en'
                     
# for each row in the csv file being read, translate the first cell
with open(ORIGINAL_FILE, "r", encoding='utf-8') as in_file:
    reader = csv.reader(in_file)
    for row in reader:
        for column in row:
            print(column + " BLABLAH")
            text = column
            # translate text
            translation = translate_client.translate(
                text,
                source_language=source,
                target_language=target)
            #row[0] = translation['translatedText']
            print(u'Translation: {}'.format(translation['translatedText']))
            translatedText = (u'Translation: {}'.format(translation['translatedText']))
            tab.insert(dict(text1=column, text2=translatedText))




