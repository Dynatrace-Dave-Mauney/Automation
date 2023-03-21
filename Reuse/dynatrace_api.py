import json
import requests
import ssl
import time

from inspect import currentframe
from json import JSONDecodeError
from requests import Response


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
        exit(1)


def get_object_list(env, token, endpoint):
    url = env + endpoint
    try:
        r = requests.get(url, params='', headers={'Authorization': 'Api-Token ' + token})
        if r.status_code not in [200]:
            print(r.status_code)
            print(r.reason)
            exit(get_line_number())
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def get_by_object_id(env, token, endpoint, object_id):
    url = env + endpoint + '/' + object_id
    try:
        r = requests.get(url, params='', headers={'Authorization': 'Api-Token ' + token})
        if r.status_code not in [200]:
            print('Error in "dynatrace_api.get_by_object_id(env, token, endpoint, object_id)" method')
            print('Endpoint: ' + endpoint)
            print('Object ID: ' + object_id)
            print('Exit code shown below is the source code line number of the exit statement invoked')
            exit(get_line_number())
        return json.loads(r.text)
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def post(env, token, endpoint: str, payload: str) -> Response:
    # In general, avoid post in favor of put so "fixed ids" can be used
    json_data = json.loads(payload)
    # print(payload)
    # Remove id if present
    # print(f'Popped: {json_data.pop("id")}')
    # json_data.pop("id")
    formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)
    url = env + endpoint
    try:
        r: Response = requests.post(url, formatted_payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        # print('Status Code: %d' % r.status_code)
        # print('Reason: %s' % r.reason)
        # if len(r.text) > 0:
        #     print(r.text)
        if r.status_code not in [200, 201, 204]:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
            error_filename = '$post_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(formatted_payload)
                name = json_data.get('name')
                if name:
                    print('Name: ' + name)
                print('Error in "dynatrace_api.post(env, token, endpoint: str, payload: str)" method')
                print('Exit code shown below is the source code line number of the exit statement invoked')
                print('See ' + error_filename + ' for more details')
            exit(get_line_number())
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def put(env, token, endpoint, object_id, payload):
    # In general, favor put over post so "fixed ids" can be used
    json_data = json.dumps(json.loads(payload), indent=4, sort_keys=False)
    url = env + endpoint + '/' + object_id
    try:
        r: Response = requests.put(url, json_data.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        if r.status_code not in [200, 201, 204]:
            error_filename = '$put_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(json_data)
                print('Error in "dynatrace_api.put(env, token, endpoint, object_id, payload)" method')
                print('Exit code shown below is the source code line number of the exit statement invoked')
                print('See ' + error_filename + ' for more details')
            exit(get_line_number())
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def put_without_id(env, token, endpoint, payload):
    json_data = json.dumps(json.loads(payload), indent=4, sort_keys=False)
    url = env + endpoint
    try:
        r: Response = requests.put(url, json_data.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        if r.status_code not in [200, 201, 204]:
            error_filename = '$put_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(json_data)
                print('Error in "dynatrace_api.put(env, token, endpoint, object_id, payload)" method')
                print('Exit code shown below is the source code line number of the exit statement invoked')
                print('See ' + error_filename + ' for more details')
            exit(get_line_number())
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def postv1(env, token, endpoint, payload):
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


def putv1(env, token, endpoint, object_id, payload):
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
    try:
        r = requests.delete(url, headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        if r.status_code not in [200, 201, 204]:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
            exit()
    except ssl.SSLError:
        print('SSL Error')

def delete_with_response(env, token, endpoint, object_id):
    url = f'{env}{endpoint}/{object_id}'
    try:
        r = requests.delete(url, headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        return r
    except ssl.SSLError:
        print('SSL Error')
