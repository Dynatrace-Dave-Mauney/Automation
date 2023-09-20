import json
import os
import requests

from Reuse import environment

# Creating an OAuth Client:
# Old UI: Person Icon > Account Settings > Pick Account if needed > Identity & access management > OAuth Clients > "Create client" button
# New UI: Person Icon > Account Management > Pick Account if needed > Identity & access management > OAuth Clients > "Create client" button
# Assign all permissions under the Account section:
# account-idm-read, account-idm-write, account-env-read, account-env-write, account-uac-read, account-uac-write,
# iam-policies-management, iam:policies:write, iam:policies:read, iam:bindings:write, iam:bindings:read,
# iam:effective-permissions:read


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


def get_platform_api(api_type, bearer_token):
    url = f'https://api.dynatrace.com/iam/v1/accounts/{account_id}/{api_type}'
    if api_type in ['environments', 'subscriptions']:
        url = f'https://api.dynatrace.com/env/v1/accounts/{account_id}/{api_type}'
    if api_type in ['time-zones', 'regions']:
        url = f'https://api.dynatrace.com/ref/v1/{api_type}'
    if api_type == 'permissions':
        url = 'https://api.dynatrace.com/ref/v1/account/permissions'

    headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        # print(r.text)
        return r
    else:
        print(f'GET Request to Account Management API {api_type} Endpoint Failed:')
        print(f'Response Status Code: {r.status_code}')
        print(f'Response Reason:      {r.reason}')
        print(f'Response Text:        {r.text}')
        print("Exiting Program")
        exit(1)


def process():
    # account_id = os.getenv('ACCOUNTID')
    client_secret = os.getenv('CLIENT_SECRET')
    client_id = os.getenv('CLIENT_ID')

    # account_id = environment.get_configuration('get_bearer_token_personal_account_id')
    client_id = environment.get_configuration('get_bearer_token_personal_client_id')
    client_secret = environment.get_configuration('get_bearer_token_personal_client_secret')

    # Always needed minimal scope for new platform
    # scope = 'app-engine:apps:run'
    # scope += ' document:documents:read'
    scope = 'app-engine:apps:run document:documents:read document:documents:delete document:environment-shares:read document:environment-shares:write document:environment-shares:claim document:environment-shares:delete document:direct-shares:read document:direct-shares:write document:direct-shares:delete'

    print('Masked environment variables:')
    print(f'client_secret: {client_secret[:5]}*{client_secret[70:]}')
    print(f'client_id: {client_id[:10]}*')
    print(f'scope: {scope}')

    get_oauth_bearer_token(client_id, client_secret, scope)


if __name__ == '__main__':
    process()
