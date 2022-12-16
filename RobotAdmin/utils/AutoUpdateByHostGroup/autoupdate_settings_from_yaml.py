# Token Permissions Required:
# entities.read (Read entities)
# ReadConfig (Read configuration)
# WriteConfig (Write configuration)

import json
import os
import requests
import ssl
import urllib.parse
import yaml

host_group_lookup = {}
host_lookup = {}

def process():
    with open('autoupdate.yaml', 'r') as file:
        document = file.read()
        yaml_data = yaml.load(document, Loader=yaml.FullLoader)

    settings = yaml_data.get('settings')

    for setting in settings:
        setting_value = setting.get('setting')
        if setting_value not in ['INHERITED', 'ENABLED' , 'DISABLED']:
            print('Aborting.  Unsupported setting value: ' + setting_value)
            exit(1)

        host_groups = setting.get('hostgroups')
        hosts = setting.get('hosts')

        # print('Setting:     ' + setting_value)
        # print('Host Groups: ' + str(host_groups))
        # print('Hosts:       ' + str(hosts))

        if host_groups:
            load_host_group_lookup(host_groups)
            for host_group in host_groups:
                change_host_group_autoupdate_setting(host_group, setting_value)

        if hosts:
            load_host_lookup(hosts)
            for host in hosts:
                change_host_autoupdate_setting(host, setting_value)

def change_host_group_autoupdate_setting(host_group, setting):
    host_group_id = host_group_lookup[host_group]
    endpoint = '/api/config/v1/hostgroups/' + host_group_id + '/autoupdate'
    settings_json_list = get_rest_api_json(env, token, endpoint, '')
    settings_json = settings_json_list[0]
    old_setting = settings_json.get('setting')
    version = settings_json.get('version')
    payload = {'setting': setting, 'version': version}
    put(env, endpoint, token, host_group_id, json.dumps(payload))
    print('Autoupdate setting changed from ' + old_setting + ' to ' + setting + ' for host group ' + host_group + '(' + host_group_id + ')')


def change_host_autoupdate_setting(host, setting):
    host_id = host_lookup[host]
    endpoint = '/api/config/v1/hosts/' + host_id + '/autoupdate'
    settings_json_list = get_rest_api_json(env, token, endpoint, '')
    settings_json = settings_json_list[0]
    old_setting = settings_json.get('setting')
    version = settings_json.get('version')
    payload = {'setting': setting, 'version': version}
    put(env, endpoint, token, host_id, json.dumps(payload))
    print('Autoupdate setting changed from ' + old_setting + ' to ' + setting + ' for host ' + host + '(' + host_id + ')')


def put(env, endpoint, token, object_id, payload):
    url = env + endpoint
    # print('PUT: ' + url)
    # print('payload: ' + payload)
    try:
        r = requests.put(url, payload.encode('utf-8'),
                         headers={'Authorization': 'Api-Token ' + token,
                                  'Content-Type': 'application/json; charset=utf-8'})
        # print('Status Code: %d' % r.status_code)
        # print('Reason: %s' % r.reason)
        # if len(r.text) > 0:
        #     print(r.text)
        if r.status_code not in [200, 201, 204]:
            print('Aborting due to Unexpected Status Code: %d' % r.status_code)
            print(r.reason)
            print(r.text)
            print(url)
            print(payload)
            exit(2)
    except ssl.SSLError:
        print('SSL Error')

def load_host_group_lookup(host_groups):
    global host_group_lookup

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST_GROUP)&to=-72h'
    # raw_params = 'entitySelector=type(HOST_GROUP)'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = get_rest_api_json(env, token, endpoint, params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            display_name = inner_entities_json.get('displayName')
            if display_name in host_groups:
                entity_id = inner_entities_json.get('entityId')
                host_group_lookup[display_name] = entity_id


def load_host_lookup(hosts):
    global host_lookup

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-72h'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = get_rest_api_json(env, token, endpoint, params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            display_name = inner_entities_json.get('displayName')
            if display_name in hosts:
                entity_id = inner_entities_json.get('entityId')
                host_lookup[display_name] = entity_id


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
    # print(resp.text)
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(3)

    json = resp.json()

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json) is list:
        # DEBUG:
        # print(json)
        return json

    json_list = [json]
    next_page_key = json.get('nextPageKey')

    while next_page_key is not None:
        # print(f'next_page_key: {next_page_key}')
        params = {'nextPageKey': next_page_key}
        full_url = url + endpoint
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
        # print(resp.url)

        if resp.status_code != 200:
            print('Paginated REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            exit(4)

        json = resp.json()
        # print(json)

        next_page_key = json.get('nextPageKey')
        json_list.append(json)

    return json_list


if __name__ == '__main__':
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')
    # env_name, tenant_key, token_key = ('FreeTrial1', 'FREETRIAL1_TENANT', 'ROBOT_ADMIN_FREETRIAL1_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

    print(f'Environment Name: {env_name}')
    print(f'Environment:      {env}')
    print(f'Token:            {masked_token}')

    print('')
    print('Updating OneAgent AutoUpdate from YAML')

    process()
