import pandas as pd
import requests
from pandas.io.json import json_normalize

API_KEY = "<PLEASE ADD API KEY>"
API_ENDPOINT = "<THIS IS WHERE THE END POINT GOES...>"

"""
47 - Space 2 - automated queries to power Company A databases
"""

raw = pd.read_csv('calls_1.csv' , sep=',')
raw = raw.drop(['id'] , axis = 1)

#creating the base dataframe
raw = raw[raw['external_api_client_id'] == 47].copy()

#extracting the duns number from the query_string
raw['duns']=raw.query_string.str.extract('(\d+)')

#removing unnecessary columns
raw = raw.drop(['created_at', 'external_api_client_id', 'query_string', 'variables'] , axis = 1)

#removing NaN
raw= raw.dropna()

#transforming the duns column to int
raw['duns'] = raw['duns'].astype(int)

#verification
verif = raw.isna().sum()

#net number of companies queried
raw = raw.drop_duplicates(subset ="duns" , keep = 'first' , inplace = False)

#get inventories, names and tags
bullwhip = []

def getinvnametags(duns):
    GRAPHQL_QUERY = """query getCompany($duns: String!){company(duns:$duns){displayName tags{name} balanceSheets {fiscal_year:inventories}}}"""
    request_headers= { "x-api-key": API_KEY }
    request_data = {
            "query": GRAPHQL_QUERY,
            "variables": duns
            }
    response = requests.post(API_ENDPOINT, json=request_data, headers=request_headers, timeout=30)
    response_data = response.json()
    return json_normalize(response_data)


#transforming the list into a dataframe
#seeing how many have inventories
for dun in raw['duns']:
    if len(str(dun)) == 6:
        dun = '000'+str(dun)
    elif len(str(dun)) == 7:
        dun = '00'+str(dun)
    elif len(str(dun)) == 8:
        dun = '0'+str(dun)
    else:
        dun = str(dun)
    bullwhip.append(getinvnametags({ "duns": str(dun)}))
