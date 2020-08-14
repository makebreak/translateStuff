import sqlalchemy, config, sys, csv
from sqlalchemy import create_engine, Table, Column, MetaData

# db file can be default or first argument (file name only, no path)
# db file should be in appscraper/data folder
DB_FILE = str(config.DATA_DIR / "defaultDBname.db")
if len(sys.argv)>1:
    DB_FILE = str(config.DATA_DIR / sys.argv[1])
print("Using db: ", DB_FILE)

# Connect to db with scraped data and 'detected' lang column 
engine = create_engine('sqlite:///{}'.format(DB_FILE))
conn = engine.connect()
metadata = MetaData()

android_apps = Table('android_apps', metadata, autoload=True, \
                     autoload_with=engine)

def copyEnglishToNewCols(conn): 
    # get apps with detected lang == english


    # TO DO: add array of languages
    langs = [] 
    
    # for each language, export random sample of 20 apps to csv file
    for l in langs:
        # get sample of apps in that language
        queryText = "SELECT * FROM android_apps WHERE detected=\'{lang}\' ORDER BY RANDOM() LIMIT 10".format(lang=l)
        result = conn.execute(queryText)
        
        # write to csv file 
        filename = 'sample_{lang}.csv'.format(lang=l)
        fh = open(filename, 'wb')
        outcsv = csv.writer(fh)
        outcsv.writerow(result.keys())
        outcsv.writerows(result)

    return

if __name__ == "__main__":
    copyEnglishToNewCols(conn) 
