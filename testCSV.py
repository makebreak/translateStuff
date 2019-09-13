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

#text = u'Hello, world! Where did my nose go? How inconvenient.'
# The target language
target = 'ru'

# for each row in the csv file being read
# translate the third cell
# The text to translate
for row in reader:
    print(row[3])
    text = row[3]
    # translate text
    translation = translate_client.translate(
        text,
        target_language=target)
    row[3] = translation
    print(u'Translation: {}'.format(translation['translatedText']))
    writer.writerow(row)

# translate text
#translation = translate_client.translate(
#    text,
#    target_language=target)

#print(u'Text: {}'.format(text))
#print(u'Translation: {}'.format(translation['translatedText']))

in_file.close()
out_file.close()
