from __future__ import print_function
import os
import json
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_google_sheet(spreadsheet_id, range_name):
    """ Retrieve sheet data using OAuth credentials and Google Python API. """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    #if os.path.exists('token.json'):
    #    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)


    try:
        print("HELLO1")
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        
        gsheet = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        
    except HttpError as err:
        print(err)
        
    return gsheet
    
    
def gsheet2df(gsheet):
    """ Converts Google sheet data to a Pandas DataFrame.
    Note: This script assumes that your data contains a header file on the first row!

    Also note that the Google API returns 'none' from empty cells - in order for the code
    below to work, you'll need to make sure your sheet doesn't contain empty cells,
    or update the code to account for such instances.

    """
    header = gsheet.get('values', [])[0]   # Assumes first line is header!
    values = gsheet.get('values', [])[1:]  # Everything else is data.
    if not values:
        print('No data found.')
    else:
        all_data = []
        for col_id, col_name in enumerate(header):
            column_data = []
            for row in values:
                column_data.append(row[col_id])
            ds = pd.Series(data=column_data, name=col_name)
            all_data.append(ds)
        df = pd.concat(all_data, axis=1)
        return df



#DATASET


data = open("request_main.json")
data = json.load(data)
data = data["instances"][0]

dataset = get_google_sheet('15b273timti89hJtrBRA7vbuynMz3muN0lX8EnPCU-JI', 'cleaned1')
dataset_df = gsheet2df(dataset)
#print('Dataframe size = ', dataset_df.shape)
unis = dataset_df.university.unique().tolist()
unis.remove(data["university"])
#print(len(unis))
print(data)


for i in range(len(unis)):
    other_res = {"instances":[]}
    other_vals = list(data.values())[:1] + [unis[i]] + list(data.values())[2:]
    #other_vals = list(map(lambda x: x.replace(data["university"], unis[i]), list(data.values())))
    #other_vals = data
    #other_vals["university"] = unis[i]
    
    print(other_vals)
    res= dict(zip(list(data.keys()), other_vals))
    other_res["instances"].append(res)
    print(other_res)
    with open("request_other" + str(i) + ".json", "w") as write_file:
        json.dump(other_res, write_file, indent=4)
        

