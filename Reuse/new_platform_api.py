import json
# import os
import requests

from Reuse import environment

# Creating an OAuth Client:
# Old UI: Person Icon > Account Settings > Pick Account if needed > Identity & access management > OAuth Clients > "Create client" button
# New UI: Person Icon > Account Management > Pick Account if needed > Identity & access management > OAuth Clients > "Create client" button


def get_oauth_bearer_token(client_id, client_secret, scope):
    url = 'https://sso.dynatrace.com/sso/oauth2/token'
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope
    }

    r = requests.post(url, headers=headers, data=data)
    if r.status_code == 200:
        oauth_bearer_token = json.loads(r.text)['access_token']
        return oauth_bearer_token
    else:
        print(f'POST Request to Get OAuth Bearer Token Failed:')
        print(f'Response Status Code: {r.status_code}')
        print(f'Response Reason:      {r.reason}')
        print(f'Response Text:        {r.text}')
        print("Exiting Program")
        exit(1)


def get_api(oauth_bearer_token, api_url):
    headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    r = requests.get(api_url, headers=headers)
    if r.status_code == 200:
        # print(r.text)
        return r
    else:
        print(f'GET Request to API URL {api_url} Failed:')
        print(f'Response Status Code: {r.status_code}')
        print(f'Response Reason:      {r.reason}')
        print(f'Response Text:        {r.text}')
        print('Exiting Program')
        exit(1)


if __name__ == '__main__':
    print('This module is not designed to be run standalone!')
