from inspect import currentframe
import json
import os
import requests
import ssl
import urllib.parse
from requests import Response

target_management_zones = [
    'HostGroup:Laptops',
]

# target_technologies = [
#     'apache',
#     'iis-microsoft',
#     'mysql',
#     'oracledatabase',
#     'oracleweblogic',
#     'sap',
#     'sql-microsoft',
#     'was-liberty-profile',
#     'web-sphere',
# ]

# Using an OS process for testing to guarantee only one process group is affected
target_technologies = [
    'windows',
]

# env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

tenant = os.environ.get(tenant_key)
token = os.environ.get(token_key)
env = f'https://{tenant}.live.dynatrace.com'


def process():
    entity_type = 'PROCESS_GROUP'

    process_group_to_update_list = []

    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector) + '&fields=' + urllib.parse.quote('managementZones,icon')
    entities_json_list = get_rest_api_json(env, endpoint, params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            management_zone_list = inner_entities_json.get('managementZones')
            for management_zone in management_zone_list:
                if management_zone.get('name') in target_management_zones:
                    primary_icon_type = inner_entities_json.get('icon').get('primaryIconType', '')
                    print(primary_icon_type)
                    if primary_icon_type in target_technologies:
                        print(entity_id + '|' + display_name + '|' + primary_icon_type)
                        process_group_to_update_list.append(entity_id)

    turn_on_process_group_monitoring(process_group_to_update_list)


def turn_on_process_group_monitoring(process_group_to_update_list):
    print('turn_on_process_group_monitoring(' + str(process_group_to_update_list) + ')')
    for process_group_to_update in process_group_to_update_list:
        turn_on_process_group_monitoring_setting(process_group_to_update)


def turn_on_process_group_monitoring_setting(process_group_to_update):
    print('get_process_group_monitoring_setting(' + process_group_to_update + ')')

    put_object_id_list = []
    post_payload_list = []

    endpoint = '/api/v2/settings/objects'
    params = 'schemaIds=' + urllib.parse.quote('builtin:availability.process-group-alerting') + '&scopes=' + process_group_to_update + '&fields=' + urllib.parse.quote('objectId,value')
    settings_json_list = get_rest_api_json(env, endpoint, params)
    # print(settings_json_list)
    for settings_json in settings_json_list:
        total_count = settings_json.get('totalCount', '0')
        # print('total_count:', total_count)
        # print('total_count int:', int(total_count))
        if int(total_count) > 0:
            # print('total_count > 0')
            item_list = settings_json.get('items')
            for item in item_list:
                # print(item)
                object_id = item.get('objectId')
                value = item.get('value')
                enabled = value.get('enabled', False)
                if not enabled:
                    print('PUT ' + object_id)
                    put_object_id_list.append(object_id)
        else:
            # print('total_count not > 0')
            print('POST new object')
            payload_string = '{"schemaId": "builtin:availability.process-group-alerting", "scope": "' + process_group_to_update + '", "value": {"enabled": true, "alertingMode": "ON_PGI_UNAVAILABILITY"}}'
            # print(payload_string)
            post_payload_list.append(json.loads(payload_string))

    # print(put_object_id_list)
    # print(post_payload_list)

    if put_object_id_list:
        for put_object_id in put_object_id_list:
            put(endpoint, put_object_id)

    if post_payload_list:
        post(endpoint, json.dumps(post_payload_list))


def post(endpoint, payload):
    print('post(env, endpoint, token, payload)')
    json_data = json.loads(payload)
    formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)
    url = env + endpoint
    # print('POST: ' + url)
    # print('payload: ' + json_data)
    try:
        r = requests.post(url, payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        print('Status Code: %d' % r.status_code)
        print('Reason: %s' % r.reason)
        if len(r.text) > 0:
            print(r.text)
        if r.status_code not in [200, 201, 204]:
            # print(json_data)
            error_filename = '$post_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(formatted_payload)
                if not(isinstance(json_data, list)):
                    name = json_data.get('name')
                    if name:
                        print('Name: ' + name)
                print('Error in "post(env, endpoint, token, payload)" method')
                print('Exit code shown below is the source code line number of the exit statement invoked')
                print('See ' + error_filename + ' for more details')
            exit(get_line_number())
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def put(endpoint, object_id):
    print('put(env, endpoint, token, payload)')

    payload = '{"value": {"enabled": true, "alertingMode": "ON_PGI_UNAVAILABILITY"}}'

    json_data = json.loads(payload)
    formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)
    url = env + endpoint + '/' + object_id
    # print('PUT: ' + url)
    # print('payload: ' + json_data)
    try:
        r = requests.put(url, payload.encode('utf-8'),
                         headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        print('Status Code: %d' % r.status_code)
        print('Reason: %s' % r.reason)
        if len(r.text) > 0:
            print(r.text)
        if r.status_code not in [200, 201, 204]:
            # print(json_data)
            error_filename = '$put_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(formatted_payload)
                if not(isinstance(json_data, list)):
                    name = json_data.get('name')
                    if name:
                        print('Name: ' + name)
                print('Error in "put(env, endpoint, token, payload)" method')
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


def delete(endpoint, object_id):
    url = env + endpoint + '/' + object_id
    try:
        r: Response = requests.delete(url, headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        if r.status_code == 204:
            print('Deleted ' + object_id + ' (' + endpoint + ')')
        else:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
        if r.status_code not in [200, 201, 204]:
            # print(json_data)
            print('Error in "delete(endpoint, object_id)" method')
            print('Env: ' + env)
            print('Endpoint: ' + endpoint)
            print('Token: ' + token)
            print('Object ID: ' + object_id)
            print('Exit code shown below is the source code line number of the exit statement invoked')
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def get_rest_api_json(url, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    response_json = resp.json()
    json_list = [response_json]
    next_page_key = response_json.get('nextPageKey')

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

        response_json = resp.json()
        # print(json)

        next_page_key = response_json.get('nextPageKey')
        json_list.append(response_json)

    return json_list


if __name__ == '__main__':
    # For testing POST vs PUT you may want to delete an object ID
    # delete('/api/v2/settings/objects', 'vu9U3hXa3q0AAAABACtidWlsdGluOmF2YWlsYWJpbGl0eS5wcm9jZXNzLWdyb3VwLWFsZXJ0aW5nAA1QUk9DRVNTX0dST1VQABA0RkNFQkM5RjIzQTlGRkZDACQxMTI0YjgwYS1kYTJkLTM2OGYtODNmZi1lM2U3Mzk0OGY3YzO-71TeFdrerQ')
    # delete('/api/v2/settings/objects', 'vu9U3hXa3q0AAAABACtidWlsdGluOmF2YWlsYWJpbGl0eS5wcm9jZXNzLWdyb3VwLWFsZXJ0aW5nAA1QUk9DRVNTX0dST1VQABA0RjdBMzhCRDg5MUQxMENGACQ2YTE3NmYxZC03MzU2LTMxNDMtODVjMS02YTg3ZTk1OTk2Mja-71TeFdrerQ')
    # delete('/api/v2/settings/objects', 'vu9U3hXa3q0AAAABACtidWlsdGluOmF2YWlsYWJpbGl0eS5wcm9jZXNzLWdyb3VwLWFsZXJ0aW5nAA1QUk9DRVNTX0dST1VQABAzRjQyODNBMDMwQ0I4Qjg0ACRhZjJlYWRiOS03YjY5LTNlODQtOTllOS03MDQxMzBiZDUwYTO-71TeFdrerQ')
    # vu9U3hXa3q0AAAABACtidWlsdGluOmF2YWlsYWJpbGl0eS5wcm9jZXNzLWdyb3VwLWFsZXJ0aW5nAA1QUk9DRVNTX0dST1VQABAzRjQyODNBMDMwQ0I4Qjg0ACRhZjJlYWRiOS03YjY5LTNlODQtOTllOS03MDQxMzBiZDUwYTO-71TeFdrerQ
    process()
