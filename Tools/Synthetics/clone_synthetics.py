"""

For safety, a clone will only be done for a specific synthetic.

Remove the if statement to clone all synthetics.

"""

import json
import os
import ssl
import requests
from inspect import currentframe
from requests import Response


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    json_data = resp.json()

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json_data) is list:
        # DEBUG:
        # print(json)
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
        # print(json)

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def get_by_object_id(env, token, endpoint, object_id):
    url = env + endpoint + '/' + object_id
    try:
        r = requests.get(url, params='', headers={'Authorization': 'Api-Token ' + token})
        if r.status_code not in [200]:
            print('Error in "get_by_object_id(endpoint, object_id)" method')
            print('Endpoint: ' + endpoint)
            print('Object ID: ' + object_id)
            print('Exit code shown below is the source code line number of the exit statement invoked')
            exit(get_line_number())
        return json.loads(r.text)
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def post(env, token, endpoint: str, payload: str) -> Response:
    json_data = json.loads(payload)
    formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)
    url = env + endpoint
    try:
        r: Response = requests.post(url, payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
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
                print('Error in "post(endpoint, payload)" method')
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


def process(source_env, source_token, target_env, target_token):
    endpoint = '/api/v1/synthetic/monitors'
    params = ''
    monitors_json_list = get_rest_api_json(source_env, source_token, endpoint, params)
    for monitors_json in monitors_json_list:
        inner_monitors_json_list = monitors_json.get('monitors')
        for inner_monitors_json in inner_monitors_json_list:
            entity_id = inner_monitors_json.get('entityId')
            monitor_name = inner_monitors_json.get('name')
            # if entity_id == 'HTTP_CHECK-59CB6082C98678C5':  # No Locations, for testing the location default
            if entity_id == 'SYNTHETIC_TEST-6ED223C2D0114F83':  # Has locations, is enabled, and works fine
                monitor = get_by_object_id(source_env, source_token, endpoint, entity_id)
                locations = monitor.get('locations')
                # Disable monitor to avoid runs until ready
                monitor['enabled'] = False
                # If no locations, use AWS N. Virgina to avoid a 404 on the POST
                if not locations:
                    monitor['locations'] = ['GEOLOCATION-9999453BE4BDB3CD']
                response = post(target_env, target_token, endpoint, json.dumps(monitor, indent=4, sort_keys=False))
                new_entity_id = json.loads(response.text).get('entityId')
                print(f'Cloned {monitor_name} ({entity_id}) from {source_env} to {target_env} with same name and new entity id of {new_entity_id}')


def main():
    env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    source_tenant = os.environ.get(tenant_key)
    source_token = os.environ.get(token_key)
    source_env = f'https://{source_tenant}.live.dynatrace.com'

    env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')
    target_tenant = os.environ.get(tenant_key)
    target_token = os.environ.get(token_key)
    target_env = f'https://{target_tenant}.live.dynatrace.com'
    process(source_env, source_token, target_env, target_token)


if __name__ == '__main__':
    main()
