# Data Extraction from USPTO PatentsView using API Calls

# Setup
import pandas as pd
import json
import requests
import os
api_key = "USPTO PATENTSVIEW API KEY"
base_url = 'https://search.patentsview.org' # this is the same for all endpoints
endpoint = 'api/v1/patent'
special_keys = {
    'api/v1/ipc'                      : 'ipcr',
    'api/v1/wipo'                     : 'wipo',
}

# Use API to get json
def response_key(endpoint:str) -> str:
    endpoint = endpoint.rstrip('/')
    leaf = endpoint.split('/')[-1]
    if leaf in special_keys:
        return special_keys[leaf]
    elif leaf.endswith('s'):
        return leaf + 'es'
    else:
        return leaf + 's'
    
# Error Handler
def handle_request_error(response):
    if response.status_code == 400:
        x_header_value = response.headers.get("X-Status-Reason")
        if x_header_value:
            print(f"Error: {x_header_value}")
        else:
            print("400 Bad Request: No X-Status-Reason found")
        exit(1)
    else:
        response.raise_for_status()

# GET requests:
def make_get_request(endpoint, param_dict):
    param_string = "&".join([f"{param_name}={json.dumps(param_val)}" for param_name, param_val in param_dict.items()])
    # note the json.dumps to ensure strings are surrounded by double quotes instead of single
    # the api will not accept single quotes
    query_url = f"{base_url}/{endpoint.strip('/')}/?{param_string}"
    response = requests.get(query_url, headers={"X-Api-Key": api_key})
    handle_request_error(response)
    return response

# Query
param_dict = {
    "f" : ["patent_id", "patent_title", "patent_date", 'applicants', 'assignees.assignee_organization', 'cpc_at_issue.cpc_group', 'cpc_current.cpc_group'], # Fields (Columns) -> list
    "q" : {"_and":[{"patent_id":["D345393","10905426","11172927"]}, {"_text_any": {"patent_title":"Detachable"}}]} # Query -> dict
    "s" : [{"patent_id":"asc"}], # Sorting -> list of dict
    "o" : {"size": 200} # Options -> dict
}

response = make_get_request(endpoint, param_dict)
response_unpacked = pd.DataFrame(response.json()[response_key(endpoint)])
response_unpacked.head()
