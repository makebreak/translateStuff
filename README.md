# translateStuff
use Google translate API to translate stuff 

Translate from one db to another. 
Set databases in config.py. 

Run translateSelection.py with languages as parameters:
source = sys.argv[1]
country = sys.argv[2]
target = sys.argv[3]

Before running, you need to set up google cloud SDK. 

See also:
Translation API: https://googleapis.dev/python/translation/latest/client.html
v3 API: https://googleapis.dev/python/translation/latest/gapic/v3beta1/api.html
https://cloud.google.com/translate/docs/reference/rpc/google.cloud.translation.v3beta1

https://github.com/googleapis/google-cloud-python/blob/master/translate/google/cloud/translate_v3beta1/gapic/translation_service_client.py

