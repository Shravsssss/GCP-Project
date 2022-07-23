from __future__ import print_function
import json
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools

SCOPES = "https://www.googleapis.com/auth/forms.responses.readonly"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

store = file.Storage('token.json')
creds = None
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = discovery.build('forms', 'v1', http=creds.authorize(
    Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)

# Prints the responses of your specified form:
form_id = '12H2HZhHhGUKIAoiXNOWQYSyvllWSVjQRsc5_tQQxKPo'
result = service.forms().responses().list(formId=form_id).execute()


headers = ['grescore','university','undergradscore','course','year','engtest','testscore','name','workex']
res_values = []
for ques in result['responses'][0]['answers'].values():
    res_values.append(ques['textAnswers']['answers'][0]['value'])
    
request = dict(zip(headers, res_values))

del request['year']
del request['engtest']
del request['name']

main_res = {"instances":[]}
main_res["instances"].append(request)
#print(main_res)

with open("request_main.json", "w") as write_file:
    json.dump(main_res, write_file, indent=4)


