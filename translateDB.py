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
target_language = 'en'
colname = 'detected'  # RC: That's a bad col name, should have been: detcted_lang or something


USAGE = "$ python {} <appstore> <db-file>".format(sys.argv[0])
### args ###
# store
store = 'android'
if len(argv) > 1:
    if (sys.argv[1] == 'android') or (sys.argv[1] == 'ios'):
        store = sys.argv[1]
        print('Store is:', store)
    else:
        raise ValueError('Invalid store argument. Default android will be used.')


# in file db to update with translated text
ORIGINAL_FILE = str(config.DATA_DIR / "crawled_apps_copy.db")
if len(sys.argv)>3:
    ORIGINAL_FILE = str(config.DATA_DIR / sys.argv[3])

# Connect to original db with scraped data 
dbApps = dataset.connect('sqlite:///{}'.format(ORIGINAL_FILE))



# translate function
def translateFunc(texts, source_language, target_language):
    """
    translate_text returns TranslateTextResponse
    texts is a list and respond with a list of translations. Default it will traslate to to english. 
    """
    try:
        response = translate_client.translate_text(
            contents=texts
            target_language_code=target_language,
            mime_type=None,
            source_language_code=source_language,
            parent=parent_code
        )
        for translation in response.translations:
            print(u'Translation: {}'.format(translation.translated_text))
        #sleep for 0.1 second 
        time.sleep(0.1)   
        return response.translations
    except Exception as e:
        print("not able to translate, error >>", e)
        # response.translations is a Translation object
        time.sleep(1)
        return None

## I am not sure I understand if this function is sufficient to check if it is
## translated or not.  A better would be test if the ttranslatetime is not
## null. Can you test it? 
def isTranslated(appid):
    """
    skip if already translated
    # column for condition for sql query (where colname = xyz)
    """
    try:
        testQuery = dbApps.query(
            "SELECT 1 from {store}_apps where appId = :appId "\
            "and {colname} = :".format(store=store, colname=colname),
            appId=appid, value=source_language
        )
        if testQuery:
            print("already translated, skipping")
            return True
        return False
    except Exception as e:
        print("probably no translated column tsummary found >> ",
              e, file=sys.stderr)
        raise ValueError(e)




if store == 'android':
    appsTable = dbApps['android_apps']
else:
    appsTable = dbApps['ios_apps']

# The target and source languages
# source will be language to be translated
# RC: this should go to a function
source_language = 'es'
try:
    langArg = sys.argv[2]
    print('Lang arg is: ', langArg)

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
                source_language = langArg
                print('Chosen language: ',dlang)
        except:
            print('could not iterate over available lang options')
    if (source_language != langArg):
        print('Invalid language argument. Spanish will be used.')
        source_language = 'es'
except:
    print('No source language specified. Spanish will be used.')
    source_language = 'es'
    raise    # RC: I would say also stop here, you cannot continue with this error.


def translate_all_apps(lang=source_language):
    # get selection of apps
    try:
        result = dbApps.query(
            "select id, appId, title, summary, description \
            from {store}_apps where {colname} = :value "\
            .format(colname=colname, store=store),
            value=source_language
        )
    except Exception as e:
        print("exists >> ", e, file=sys.stderr)
        raise  ## RC: You cannot continue after this fails

    # translate each entry and update db
    for row in result:
        if isTranslated(row['appId'])
        date1 = datetime.datetime.now()
        datestring = date1.strftime("%Y-%m-%d-%H%M%S")

        print("reading row")
        # text from db to be translated
        # for v3 API, text to be translated needs to be a list
        texts = [row['title'],
                 row['description'],
                 row['summary'] f store='android' else '']

        try:
            ttitle, tdescription, tsummary = translateFunc(app_dict)
        except Exception as e:
            print("Could not translate: {appId}".format(**row))
            continue
            #update db's android_apps table
        data = dict(
            id = row['id'],
            ttitle = ttitle,
            tdescription = tdescription,
            translationtime = datestring
        )
        if store == 'android':
            data['tsummary'] = tsummary,

        appsTable.update(data, ['id'])

if __name__ == "__main__":
    translate_all_apps()
