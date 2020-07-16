import os, file, csv, config, dataset, time, collections, sys, datetime, sqlalchemy

from sqlalchemy.sql import exists

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

#target language
target = 'en'

# translate function
def translateFunc(appdict):

    print(appdict)
    
    # translate_text returns TranslateTextResponse
    for key in appdict:
        try:
            response = translate_client.translate_text(
                contents=appdict[key],
                target_language_code=target,
                mime_type=None,
                source_language_code=source,
                parent=parent_code
            )
        except Exception as e:
            print("not able to translate, error >>", e)
        # response.translations is a Translation object
        for translation in response.translations:
            print(u'Translation: {}'.format(translation.translated_text))
            #translatedText = translation.translated_text 
            appdict[key] = translation.translated_text 
    return appdict

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
        "select id, appId, title, summary, description \
        from {store}_apps where {colname} = :value "\
        .format(colname=colname,
                store=store),
                value=source,
    )
except Exception as e:
    print("exists >> ", e, file=sys.stderr)

# translate each entry and update db
for row in result:

    # skip if already translated
    try:
        testQuery = dbApps.query( 
            "SELECT ttitle from {store}_apps\
            where appId= \'{rowId}\'\
            and {colname} = :value "\
            .format(store=store,
                    rowId=row['appId'],
                    colname=colname),
                    value=source,
        )
        testText = None 
        for entry in testQuery:
            tt = entry['ttitle']
            print(tt)
            if tt is not None:
                testText = tt
        if testText is not None:
            print("already translated, skipping")
            continue 
    except Exception as e:
        print("probably no translated column tsummary found >> ",\
              e, file=sys.stderr)
        
    date1 = datetime.datetime.now()
    datestring = date1.strftime("%Y-%m-%d-%H%M%S")
    
    print("reading row")
    # text from db to be translated
    # for v3 API, text to be translated needs to be a list
    app_dict = collections.defaultdict(list) 
    app_dict['title'].append(row['title'])
    app_dict['description'].append(row['description'])
    if store == 'android':
        app_dict['summary'].append(row['summary'])

    idtext = row['id']
    
    # translate text - call function
    translated = translateFunc(app_dict)
    ttitle = translated['title']
    tdescription = translated['description']
    tsummary = translated['summary']

    #update db's android_apps table
    if store == 'android':
        data = (dict(
            id = row['id'],
            ttitle = ttitle,
            tsummary = tsummary,
            tdescription = tdescription,
            translationtime = datestring
        ))
    else:
        data = (dict(
            id = row['id'],
            ttitle = ttitle,
            tdescription = tdescription,
            translationtime = datestring
        ))

    appsTable.update(data, ['id'])
        
    #sleep for 1 second 
    time.sleep(1)

