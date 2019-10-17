import os, file, csv, config, dataset, time, collections, sqlalchemy

# Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = file.dirname

# Imports the Google Cloud client library
from google.cloud import translate_v3beta1

# Instantiates a client
project = file.project
location = 'global' 
translate_client = translate_v3beta1.TranslationServiceClient()
parent_code = 'projects/' + project + '/locations/global' #+ location 
#translate_client.location_path(project, location)
input_configs = []
output_config = {}

# translate function
def translateFunc(text):
    #target_language_code=target
    print(text)
    # translate_text returns TranslateTextResponse
    response = translate_client.translate_text(
        contents=text,
        target_language_code=target,
        mime_type=None,
        source_language_code=source,
        parent=parent_code
    )
    # response.translations is a Tranlation object
    for translation in response.translations:
        print(u'Translation: {}'.format(translation.translated_text))
        translatedText = translation.translated_text 
        time.sleep(2) #sleep to avoid hitting rate limit
        return translatedText 

### DB ###
from sqlalchemy import select

# in file db
ORIGINAL_FILE = str(config.THIS_DIR / "in.db")

# db to write to
TRANSLATED_FILE = str(config.THIS_DIR / "out.db")

# Connect to original db with scraped data
dbConnect = dataset.connect('sqlite:///{}'.format(ORIGINAL_FILE))
appDB = dbConnect['android_apps']
appTable = appDB.table 

# Connect to db where we store translations
db = dataset.connect('sqlite:///{}'.format(TRANSLATED_FILE))
# table with translated fields
transTable = db['translated_android_apps']

# The target and source languages
source = 'pt' #{'pt':['pt']}
target = 'en'

# QUERY #
# translate each entry and write to a db

statement = appTable.select(appTable).with_only_columns([appTable.c.id,appTable.c.appId, appTable.c.title, appTable.c.summary, appTable.c.description, appTable.c.developer, appTable.c.LANG, appTable.c.COUNTRY]).where(appTable.c.LANG == %(source)s )                                                                

print(source)
print('statement is:')
print(statement)

# results
results = dbConnect.query(statement + source +')')
#result = dbApps.query('SELECT id, appId, title, summary, description, developer, LANG FROM android_apps WHERE LANG=\''+source + '\' and COUNTRY=\'es\'and id > 3682')
#and id > 8692') 
#and appId=\'com.\''

for row in results:
    print('this is a row:')
    print(row)
    # text from db to be translated
    # for v3 API, text to be translated needs to be a list
    app_dict = collections.defaultdict(list) 
    app_dict['title'].append(row['title'])
    app_dict['summaryText'].append(row['summary'])
    app_dict['descriptionText'].append(row['description'])
    
    # info not to be translated but stored in new db for reference
    idText = row['id']
    appIdText = row['appId']
    developerText = row['developer']
    langText = row['LANG']

    # TRANSLATION #
    # translate text - call function
    translatedTitleText = translateFunc(app_dict['title'])
    #print("translated Title text: " + translatedTitleText)
    translatedSummaryText = translateFunc(app_dict['summaryText'])
    #print("translated Summary text: " + translatedSummaryText)
    translatedDescriptionText = translateFunc(app_dict['descriptionText'])
    #print("translated Title text: " + translatedDescriptionText)
    
    #insert into new db's translation table
    transTable.insert(dict(oldId=idText, appId=appIdText, title=translatedTitleText, summary=translatedSummaryText, description=translatedDescriptionText, developer = developerText, LANG=langText))

    #sleep for 1 second 
    time.sleep(2)
    # may need to use timeout API method 
