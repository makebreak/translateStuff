import os, file, csv, config, dataset, time, collections, sys

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
    # response.translations is a Translation object
    for translation in response.translations:
        print(u'Translation: {}'.format(translation.translated_text))
        translatedText = translation.translated_text 
        time.sleep(2) #sleep to avoid hitting rate limit
        return translatedText 

# in file db
ORIGINAL_FILE = str(config.BASE_DIR / "crawled_apps.db")

# db to write to
SELECTION_FILE = str(config.THIS_DIR / "selection.db")
TRANSLATED_FILE = str(config.THIS_DIR / "translated_apps.db")

# Connect to original db with scraped data 
dbApps = dataset.connect('sqlite:///{}'.format(ORIGINAL_FILE))

# Connect to db where we store selection
dbSelection = dataset.connect('sqlite:///{}'.format(SELECTION_FILE))
selectionTable = dbSelection['android_apps']

# Connect to db where we store translations
db = dataset.connect('sqlite:///{}'.format(TRANSLATED_FILE))
# table with translated fields
transTable = db['android_apps']

# The target and source languages
# TO DO: make these arguments
try: source = sys.argv[1]
except: source = 'es'

try: country = sys.argv[2]
except: country = 'mx'

try: target = sys.argv[3]
except: target = 'en'

# get selection of apps
result = dbApps.query('SELECT id, appId, title, summary, description, genreId, developer, developerId, LANG, COUNTRY, permissions FROM android_apps WHERE LANG=\''+source + '\' and COUNTRY=\''+country+'\' limit 2;')

# Other sql options
# ORDER BY RANDOM() LIMIT 50 # select 50 random
#and appId IN (\'com.\')  # for selecting among list of apps
#and id > 8692') # for selecting range of apps, e.g., after a certain point 
#and appId=\'com.\'' # for selecting specific app


# insert results into selection db
# translate each entry and write to a db
for row in result:

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
    developerIdText = row['developerId']
    langText = row['LANG']
    countryText = row['COUNTRY']
    genreIdText = row['genreId']
    permissionsText = row['permissions']
    
    # translate text - call function
    translatedTitleText = translateFunc(app_dict['title'])
    #print("translated Title text: " + translatedTitleText)
    translatedSummaryText = translateFunc(app_dict['summaryText'])
    #print("translated Summary text: " + translatedSummaryText)
    translatedDescriptionText = translateFunc(app_dict['descriptionText'])
    #print("translated Title text: " + translatedDescriptionText)
    
    #insert into translated apps db's android_apps table
    transTable.insert(dict(oldId=idText, appId=appIdText, title=translatedTitleText, summary=translatedSummaryText, description=translatedDescriptionText, developer = developerText,developerId=developerIdText, LANG=langText, COUNTRY=countryText, genreId=genreIdText, permissions=permissionsText))

    #insert original language data into selection db's android_apps table
    selectionTable.insert(dict(id=idText, appId=appIdText, title=row['title'], summary=row['summary'], description=row['description'], developer = developerText, developerId=developerIdText, LANG=langText, COUNTRY=countryText, genreId=genreIdText, permissions=permissionsText))
    
    #sleep for 2 seconds 
    time.sleep(2)
    # may need to use timeout API method 
