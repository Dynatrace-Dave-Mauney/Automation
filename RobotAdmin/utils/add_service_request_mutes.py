from inspect import currentframe
import json
import os
import requests
import ssl


def post(env, endpoint, token, payload):
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
            exit(get_linenumber())
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_linenumber())


def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_linenumber())

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
        # next_page_key = next_page_key.replace('=', '%3D') # Ths does NOT help.  Also, equals are apparently fine in params.
        # print(f'next_page_key: {next_page_key}')
        params = {'nextPageKey': next_page_key}
        full_url = url + endpoint
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
        # print(resp.url)

        if resp.status_code != 200:
            print('Paginated REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            print('Exit code shown below is the source code line number of the exit statement invoked')
            exit(get_linenumber())

        json_data = resp.json()
        # print(json_data)

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def process():
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    tenable_request_already_muted_service_list = []
    tenable_request_needs_muted_service_list = []

    # For when everything is commented out below...
    pass

    item_list = []
    endpoint = '/api/v2/settings/objects'
    params = 'schemaIds=builtin%3Asettings.mutedrequests&fields=objectId%2Cvalue%2Cscope&pageSize=500'
    json_response_list = get_rest_api_json(env, token, endpoint, params)
    for json_response in json_response_list:
        item_list.extend(json_response.get('items'))

    # print(item_list)

    for item in item_list:
        # print(item)
        # object_id = item.get('objectId')
        # print('object_id: ' + object_id)
        # value = item.get('value')
        scope = item.get('scope')
        # print('value: ' + str(value))
        # print('scope: ' + scope)

        muted_request_list = item.get('value').get('mutedRequestNames', [])
        if 'Tenable Request' in muted_request_list:
            tenable_request_already_muted_service_list.append(scope)

    # print('tenable_request_already_muted_service_list size: ' + str(len(tenable_request_already_muted_service_list)))
    # print('tenable_request_already_muted_service_list: ' + str(tenable_request_already_muted_service_list))

    endpoint = '/api/v2/entities'
    params = 'entitySelector=type%28SERVICE%29&fields=properties.SERVICE_TYPE&from=now-1y&pageSize=4000'

    service_list = []
    json_response_list = get_rest_api_json(env, token, endpoint, params)
    for json_response in json_response_list:
        service_list.extend(json_response.get('entities'))

    for service in service_list:
        service_id = service.get('entityId')
        service_type = service.get('properties').get('serviceType')
        # print(service)
        if service_type == 'WEB_REQUEST_SERVICE' or service_type == 'WEB_SERVICE':
            if service_id not in tenable_request_already_muted_service_list:
                # service_display_name = service.get('displayName')
                # print(service_id + ':' + service_display_name)
                tenable_request_needs_muted_service_list.append(service_id)

    # print(tenable_request_needs_muted_service_list)

    payload_list = []
    for tenable_request_needs_muted_service in tenable_request_needs_muted_service_list:
        # print(tenable_request_needs_muted_service)
        endpoint = '/api/v2/settings/objects'
        payload_list.append({"schemaId": "builtin:settings.mutedrequests", "scope": tenable_request_needs_muted_service, "value": {"mutedRequestNames": ["Tenable Request"]}})

    payload_list_size = len(payload_list)
    if payload_list_size > 0:
        # The API call cannot handle too many requests in a single list, so...
        # partition the list using list comprehension
        partition_size = 1000
        partitioned_payload_list = [payload_list[i:i + partition_size] for i in range(0, len(payload_list), partition_size)]
        # print(partitioned_payload_list)
        for partition in partitioned_payload_list:
            # print(partition)
            post(env, endpoint, token, json.dumps(partition))
    else:
        print('No services need mute added at this time')


if __name__ == '__main__':
    process()
