import random
import requests
import ssl
import time

from functools import partial

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

    fn = partial(requests.post, url, headers=headers, data=data)
    r = retry_with_backoff(fn)
    if r.status_code == 200:
        oauth_bearer_token = r.json()['access_token']
        return oauth_bearer_token
    else:
        print(f'POST Request to Get OAuth Bearer Token Failed:')
        print(f'Response Status Code: {r.status_code}')
        print(f'Response Reason:      {r.reason}')
        print(f'Response Text:        {r.text}')
        print("Exiting Program")
        exit(1)


def get_account_management_api(oauth_bearer_token, api_type, **kwargs):
    account_id = None
    if kwargs:
        account_id = kwargs.get('account_id')

    url = f'https://api.dynatrace.com/iam/v1/accounts/{account_id}/{api_type}'
    if api_type in ['environments', 'subscriptions']:
        url = f'https://api.dynatrace.com/env/v1/accounts/{account_id}/{api_type}'
    if api_type in ['time-zones', 'regions']:
        url = f'https://api.dynatrace.com/ref/v1/{api_type}'
    if api_type == 'permissions':
        url = 'https://api.dynatrace.com/ref/v1/account/permissions'

    return get(oauth_bearer_token, url)


def get(oauth_bearer_token, api_url):
    headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    fn = partial(requests.get, api_url, headers=headers)
    r = retry_with_backoff(fn)

    if r.status_code == 200:
        return r
    else:
        print(f'GET Request to API URL {api_url} Failed:')
        print(f'Response Status Code: {r.status_code}')
        print(f'Response Reason:      {r.reason}')
        print(f'Response Text:        {r.text}')
        print('Exiting Program')
        exit(1)


def delete(oauth_bearer_token, api_url, **kwargs):
    if kwargs:
        params = kwargs.get('params')
    else:
        params = ''

    headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    try:
        fn = partial(requests.delete, api_url, headers=headers, params=params)
        r = retry_with_backoff(fn)
        return r
    except ssl.SSLError:
        print('Error in "user_management_api.delete(oauth_bearer_token, api_url, object_id)" method')
        print('SSL Error')


def post(oauth_bearer_token, api_url, payload):
    headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    try:
        fn = partial(requests.post, api_url, payload, headers=headers)
        r = retry_with_backoff(fn)

        if r.status_code not in [200, 201, 204]:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
            error_filename = '$post_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(payload)
                try:
                    name = payload.get('name')
                    if name:
                        print('Name: ' + name)
                except AttributeError:
                    print(payload)
                print('Error in "user_management_api.post(oauth_bearer_token, api_url, payload)" method')
                print('See ' + error_filename + ' for more details')
            exit(1)
        return r
    except ssl.SSLError:
        print('Error in "user_management_api.post(oauth_bearer_token, api_url, payload)" method')
        raise


def retry_with_backoff(fn, retries=5, backoff_in_seconds=1):
    """Simple exponential backoff implementation from https://keestalkstech.com/2021/03/python-utility-function-retry-with-exponential-backoff/
    with minor modifications (specify exceptions handled, modified formatting)"""
    x = 0
    while True:
        retry = False
        r = None
        try:
            r = fn()
            if r.status_code == 504:
                print('Retry due to 504: Gateway Timeout')
                retry = True
            if r.status_code == 500 and ('ECONNRESET' in r.text or 'socket hang up' in r.text):
                print(f'Retry due to 500: {r.text}')
                retry = True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, ConnectionError, ConnectionResetError, TimeoutError):
            print('Retry due to an exception')
            retry = True

        if retry:
            if x == retries:
                print(f'Retried with exponential backoff {retries} times, but could not recover.')
                raise

            sleep = (backoff_in_seconds * 2 ** x + random.uniform(0, 1))
            time.sleep(sleep)
            x += 1
            print(f'Retry number {x} with backoff of {sleep} seconds...')
        else:
            return r


if __name__ == '__main__':
    print('This module is not designed to be run standalone!')
