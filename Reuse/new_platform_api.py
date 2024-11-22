# import json
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

    # r = requests.post(url, headers=headers, data=data)
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


def get(oauth_bearer_token, api_url, params):
    # print(f'get({oauth_bearer_token}, {api_url}, {params}')
    headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    # r = requests.get(api_url, headers=headers, params=params)
    fn = partial(requests.get, api_url, headers=headers, params=params)
    r = retry_with_backoff(fn)

    if r.status_code == 200:
        # print(r.text)
        return r
    else:
        print(f'GET Request to API URL {api_url} Failed:')
        print(f'Response Status Code: {r.status_code}')
        print(f'Response Reason:      {r.reason}')
        print(f'Response Text:        {r.text}')
        exit(1)


def post_multipart_form_data(api_url, files, params, headers):
    try:
        # r = requests.post(api_url, files=files, params=params, headers=headers)
        fn = partial(requests.post, api_url, files=files, headers=headers, params=params)
        r = retry_with_backoff(fn)

        if r.status_code not in [200, 201, 204]:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
                print('Error in "post_multipart_form_data(api_url, files, params, headers)" method')
            exit(1)
        return r
    except ssl.SSLError:
        print('Error in "post_multipart_form_data(api_url, files, params, headers)" method')
        raise


def put_multipart_form_data(api_url, files, params, headers):
    # print(f"put_multipart_form_data({api_url}, {files}, {params}, {headers})")
    try:
        # r = requests.put(api_url, files=files, params=params, headers=headers)
        fn = partial(requests.put, api_url, files=files, headers=headers, params=params)
        r = retry_with_backoff(fn)

        if r.status_code not in [200, 201, 204]:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
                print('Error in "post_multipart_form_data(api_url, files, params, headers)" method')
            exit(1)
        return r
    except ssl.SSLError:
        print('Error in "put_multipart_form_data(api_url, files, params, headers)" method')
        raise


def delete(oauth_bearer_token, api_url, params):
    headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    try:
        # r = requests.delete(api_url, headers=headers, params=params)
        fn = partial(requests.delete, api_url, headers=headers, params=params)
        r = retry_with_backoff(fn)
        return r
    except ssl.SSLError:
        print('Error in "new_platform_api.delete(oauth_bearer_token, api_url, object_id)" method')
        print('SSL Error')


def post(oauth_bearer_token, api_url, payload):
    headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    try:
        # r = requests.post(api_url, payload, headers=headers)
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
                print('Error in "new_platform_api.post(oauth_bearer_token, api_url, payload)" method')
                print('See ' + error_filename + ' for more details')
            exit(1)
        return r
    except ssl.SSLError:
        print('Error in "new_platform_api.post(oauth_bearer_token, api_url, payload)" method')
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
