import requests
import ssl
import time

from json import JSONDecodeError


def get(url, token, endpoint, params):
    # print(f'get({url}, {endpoint}, {params})')
    full_url = url + endpoint
    try:
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token}, timeout=60.0)
    except (ConnectionError, TimeoutError):
        print('Sleeping 30 seconds before retrying due to connection or timeout error...')
        time.sleep(30)
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})

    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    try:
        json_data = resp.json()

        # Some json is just a list of dictionaries.
        # Config V1 AWS Credentials is the only example I am aware of.
        # For these, I have never seen pagination.
        if type(json_data) is list:
            # DEBUG:
            # print(json_data)
            return json_data

        json_list = [json_data]
        next_page_key = json_data.get('nextPageKey')

        while next_page_key is not None:
            # print(f'next_page_key: {next_page_key}')
            params = {'nextPageKey': next_page_key}
            full_url = url + endpoint
            resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
            # print(resp.url)

            if resp.status_code != 200:
                print('Paginated REST API Call Failed!')
                print(f'GET {full_url} {resp.status_code} - {resp.reason}')
                exit(1)

            json_data = resp.json()
            # print(json_data)

            next_page_key = json_data.get('nextPageKey')
            json_list.append(json_data)

        return json_list

    except JSONDecodeError:
        print('JSON decode error. Response: ')
        print(resp)
        print(resp.text)


def post(env, token, endpoint, payload):
    url = env + endpoint
    print('POST: ' + url)
    print('payload: ' + payload)
    try:
        r = requests.post(url, payload.encode('utf-8'),
                          headers={'Authorization': 'Api-Token ' + token,
                                   'Content-Type': 'application/json; charset=utf-8'})
        print('Status Code: %d' % r.status_code)
        print('Reason: %s' % r.reason)
        if len(r.text) > 0:
            print(r.text)
        if r.status_code not in [200, 201, 204]:
            exit()
    except ssl.SSLError:
        print('SSL Error')


def post_plain_text(env, token, endpoint, payload):
    url = env + endpoint
    print('POST: ' + url)
    print('payload: ' + payload)
    try:
        r = requests.post(url, payload, headers={'Authorization': 'Api-Token ' + token, 'accept':  '*/*', 'Content-Type': 'text/plain; charset=utf-8'})
        print('Status Code: %d' % r.status_code)
        print('Reason: %s' % r.reason)
        if len(r.text) > 0:
            print(r.text)
        if r.status_code not in [200, 201, 202, 204]:
            exit()
    except ssl.SSLError:
        print('SSL Error')


def put(env, token, endpoint, object_id, payload):
    url = env + endpoint + '/' + object_id
    print('PUT: ' + url)
    print('payload: ' + payload)
    try:
        r = requests.put(url, payload.encode('utf-8'),
                         headers={'Authorization': 'Api-Token ' + token,
                                  'Content-Type': 'application/json; charset=utf-8'})
        print('Status Code: %d' % r.status_code)
        print('Reason: %s' % r.reason)
        if len(r.text) > 0:
            print(r.text)
        if r.status_code not in [200, 201, 204]:
            exit()
    except ssl.SSLError:
        print('SSL Error')


def delete(env, token, endpoint, object_id):
    url = f'{env}{endpoint}/{object_id}'
    print('DELETE: ' + url)
    try:
        r = requests.delete(url, headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        print('Status Code: %d' % r.status_code)
        print('Reason: %s' % r.reason)
        if len(r.text) > 0:
            print(r.text)
        if r.status_code not in [200, 201, 204]:
            exit()
    except ssl.SSLError:
        print('SSL Error')

