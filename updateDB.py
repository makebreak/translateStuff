import os, file, csv, config, dataset, time, collections, sys, datetime

# Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = file.dirname

# Imports the Google Cloud client library
from google.cloud import translate_v3

# Instantiates a client
project = file.project
location = 'global' 
translate_client = translate_v3.TranslationServiceClient()
parent_code = 'projects/' + project + '/locations/global' #+ location 
#translate_client.location_path(project, location)
input_configs = []
output_config = {}

# translate function
def translateFunc(text):

    print(text)

    # translate_text returns TranslateTextResponse
    response = translate_client.translate_text(
        contents=text,
        target_language_code=target,
        mime_type=None,
        source_language_code=source,
        parent=parent_code
    )

    # response.translations is a Translation object
    for translation in response.translations:
        print(u'Translation: {}'.format(translation.translated_text))
        translatedText = translation.translated_text 
        time.sleep(2) #sleep to avoid hitting rate limit
        return translatedText 

# in file db to update with translated text
ORIGINAL_FILE = str(config.BASE_DIR / "crawled_apps_copy.db")

# Connect to original db with scraped data 
dbApps = dataset.connect('sqlite:///{}'.format(ORIGINAL_FILE))
if store = 'android':
    appsTable = dbApps['android_apps']
else:
    appsTable = dbApps['ios_apps']

# The target and source languages
try: source = sys.argv[1]
except: source = 'es'

try: country = sys.argv[2]
except: country = 'mx'

try: store = sys.argv[3]
except: store = 'android'

#try: target = sys.argv[4]
#except: target = 'en'
target = 'en'

# get selection of apps
if store = 'android':
    result = dbApps.query('SELECT id, appId, title, summary, description, LANG, COUNTRY FROM android_apps WHERE LANG={} and COUNTRY={};').format(source, country)
else:
    result = dbApps.query('SELECT id, appId, title, description, LANG, COUNTRY FROM ios_apps WHERE LANG={} and COUNTRY={};').format(source, country)

date1 = datetime.datetime.now()
datestring = date1.strftime("%Y-%m-%d-%H%M%S")

# translate each entry and update db
for row in result:

    # text from db to be translated
    # for v3 API, text to be translated needs to be a list
    app_dict = collections.defaultdict(list) 
    app_dict['title'].append(row['title'])
    app_dict['descriptionText'].append(row['description'])
    if store = 'android':
        app_dict['summaryText'].append(row['summary'])

    idText = row['id']
    
    # translate text - call function
    translatedTitleText = translateFunc(app_dict['title'])
    print("translated Title text: " + translatedTitleText)
    translatedSummaryText = translateFunc(app_dict['summaryText'])
    print("translated Summary text: " + translatedSummaryText)
    translatedDescriptionText = translateFunc(app_dict['descriptionText'])
    print("translated Title text: " + translatedDescriptionText)
    
    #update db's android_apps table
    if store = 'android':
        data = (dict(id=idText, title=translatedTitleText, summary=translatedSummaryText, description=translatedDescriptionText, TranslationTime=datestring))
    else:
        data = (dict(id=idText, title=translatedTitleText, summary=translatedSummaryText, description=translatedDescriptionText, TranslationTime=datestring))

    appsTable.update(data, ['id'])
        
    #sleep for 2 seconds 
    time.sleep(1)
    # may need to use timeout API method 
