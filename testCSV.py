import os
import file 
import csv
import config

# read and write csv file code
ORIGINAL_FILE = str(config.THIS_DIR / "in.csv")
in_file = open(ORIGINAL_FILE, "r", encoding='utf-8') 
reader = csv.reader(in_file)
TRANSLATED_FILE = str(config.THIS_DIR / "out.csv")
out_file = open(TRANSLATED_FILE, "w", encoding='utf-8')
writer = csv.writer(out_file)

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
for row in reader:
#    for column in row:
    print(row[0])
    text = row[0]
    # translate text
    translation = translate_client.translate(
        text,
        source_language=source,
        target_language=target)
    row[0] = translation['translatedText']
    print(u'Translation: {}'.format(translation['translatedText']))
    writer.writerow(row)

in_file.close()
out_file.close()
