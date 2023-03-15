# Token Permissions Required:
# entities.read (Read entities)
# ReadConfig (Read configuration)
# WriteConfig (Write configuration)

import json
import requests
import ssl
import urllib.parse
import yaml

from Reuse import dynatrace_api
from Reuse import environment


host_group_lookup = {}
host_lookup = {}


def process():
    with open('autoupdate.yaml', 'r') as file:
        document = file.read()
        yaml_data = yaml.load(document, Loader=yaml.FullLoader)

    settings = yaml_data.get('settings')

    for setting in settings:
        setting_value = setting.get('setting')
        if setting_value not in ['INHERITED', 'ENABLED', 'DISABLED']:
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
    settings_json_list = dynatrace_api.get(env, token, endpoint, '')
    settings_json = settings_json_list[0]
    old_setting = settings_json.get('setting')
    version = settings_json.get('version')
    payload = {'setting': setting, 'version': version}
    put(env, endpoint, token, host_group_id, json.dumps(payload))
    print('Autoupdate setting changed from ' + old_setting + ' to ' + setting + ' for host group ' + host_group + '(' + host_group_id + ')')


def change_host_autoupdate_setting(host, setting):
    host_id = host_lookup[host]
    endpoint = '/api/config/v1/hosts/' + host_id + '/autoupdate'
    settings_json_list = dynatrace_api.get(env, token, endpoint, '')
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
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
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
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            display_name = inner_entities_json.get('displayName')
            if display_name in hosts:
                entity_id = inner_entities_json.get('entityId')
                host_lookup[display_name] = entity_id


if __name__ == '__main__':
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    print('Updating OneAgent AutoUpdate from YAML')

    process()
