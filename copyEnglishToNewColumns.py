import sqlalchemy, config, sys
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
    result = conn.execute("select * from android_apps where detected='en'")

    # for each app, update translated entries with existing english values
    for row in result:
        stmt = android_apps.update().where(android_apps.c.id==row['id']).\
               values(ttitle=android_apps.c.title, \
                      tsummary=android_apps.c.summary, \
                      tdescription=android_apps.c.description)
        conn.execute(stmt)

    return

if __name__ == "__main__":
    copyEnglishToNewCols(conn) 
