import os, file, csv, config, dataset, time

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
# table with translated fields
transTable = db['translated_android_apps']

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
result = dbApps.query('SELECT id, appId, title, summary, description, developer FROM android_apps WHERE LANG=\''+source + '\'')
#for app in appTable:
for row in result:
    # text from db to be translated 
    titleText = row['title']
    print(titleText)
    summaryText=row['summary']
    descriptionText = row['description']
    
    # info not to be translated but stored in new db for reference
    idText = row['id']
    appIdText = row['appId']
    developerText = row['developer']

    # translate text - call function
    translatedTitleText = translateFunc(titleText)
    #print("translated Title text: " + translatedTitleText)
    translatedSummaryText = translateFunc(summaryText)
    translatedDescriptionText = translateFunc(descriptionText)
    
    #insert into new db's translation table
    transTable.insert(dict(oldId=idText, appId=appIdText, title=translatedTitleText, summary=translatedSummaryText, description=translatedDescriptionText, developer = developerText))

    #sleep for 1 second 
    time.sleep(1)
