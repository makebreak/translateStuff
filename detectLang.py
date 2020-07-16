import os, file, csv, config, dataset, time, collections, sys, datetime, sqlalchemy

from sqlalchemy.sql import exists
from collections import Counter

# Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = file.dirname

# Imports the Google Cloud client library
from google.cloud import translate_v3

# Instantiates a client
project = file.project
location = 'global' 
translate_client = translate_v3.TranslationServiceClient()
parent_code = 'projects/' + project + '/locations/global' #+ location 
input_configs = []
output_config = {}

# translate function
def detectFunc(listedItems):

    print(listedItems)
    
    #list of detected langs
    langList=[]
    
    # translate_text returns TranslateTextResponse
    for item in listedItems:
        print(type(item))
        try:
            response = translate_client.detect_language(
                parent=parent_code,
                content=item,
                mime_type=None
            )
        except Exception as e:
            print("not able to process for detection; error >>", e)
        # DetectLanguageResponse object
        for result in response.languages:
            print(u'Text: {}'.format(item))
            print(result)
            currentLang = result.language_code
            print("Language code: ", currentLang)
            langList.append(currentLang)

        return langList

# in file db to update with translated text
ORIGINAL_File = ""
try: ORIGINAL_FILE = str(config.DATA_DIR / sys.argv[3])
except: ORIGINAL_FILE = str(config.DATA_DIR / "crawled_apps_copy.db")

# Connect to original db with scraped data 
dbApps = dataset.connect('sqlite:///{}'.format(ORIGINAL_FILE))

# column for condition for sql query (where colname = xyz) 
colname = 'detected'

### args ###
# store
try:
    if (sys.argv[1] == 'android') or (sys.argv[1] == 'ios'):
        store = sys.argv[1]
        print('Store is:', store)
    else:
        print('Invalid store argument. Default android will be used.')
except: store = 'android'

if store == 'android':
    appsTable = dbApps['android_apps']
else:
    appsTable = dbApps['ios_apps']

# The target and source languages
# source will be language to be translated
try:
    langArg = sys.argv[2]
    print('Lang arg is: ',langArg)

    # get all possible valid inputs from relevant column
    queryText = 'SELECT DISTINCT {colname} FROM {store}_apps;'\
                .format(colname=colname, store=store)
    print('Query: ',queryText)
    langOptions = dbApps.query(queryText)
    # validate lang arg input by user
    for row in langOptions:
        try:
            print(row)
            dlang = row[colname]
            print(dlang)
            if (dlang == langArg):
                source = langArg
                print('Chosen language: ',dlang)
        except:
            print('could not iterate over available lang options')
    if (source != langArg):
        print('Invalid language argument. Spanish will be used.')
        source = 'es'
except:
    print('No source language specified. Spanish will be used.')
    source = 'es'

# get selection of apps
try:
    result = dbApps.query(
        "select id, appId, title\
        from {store}_apps where {colname} = :value "\
        .format(colname=colname,
                store=store),
                value=source,
    )
except Exception as e:
    print("exists >> ", e, file=sys.stderr)

# detect language for each entry #and update db
for row in result:
        
    print("reading row")
    # text from db to be used for detection

    # text to be detected needs to be a string
    # create array of strings or concatenate strings into one entry
    entryList = []
    #add each field to list
    # item 0 
    entryList.append(row['title'])
    #entryList.append(row['description'])
    #if store == 'android':
    #    entryList.append(row['summary'])

    idtext = row['id']
    
    # detect text - call function
    detected = detectFunc(entryList)
    # take most common language in returned list of languages
    rowLanguage = Counter(detected).most_common()[0][0]

    print("Language detected: ", rowLanguage)
    
    #update db's android_apps table
    #if store == 'android':
    #    data = (dict(
    #        id = row['id'],
    #        ttitle = ttitle,
    #        tsummary = tsummary,
    #        tdescription = tdescription,
    #        translationtime = datestring
    #    ))
    #else:
    #    data = (dict(
    #        id = row['id'],
    #        ttitle = ttitle,
    #        tdescription = tdescription,
    #        translationtime = datestring
    #    ))

    #appsTable.update(data, ['id'])
        
    #sleep for 1 second 
    time.sleep(1)

