# Token Permissions Required:
# entities.read (Read entities)
# ReadConfig (Read configuration)
# WriteConfig (Write configuration)

import json
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
    settings_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    settings_json = settings_json_list[0]
    old_setting = settings_json.get('setting')
    version = settings_json.get('version')
    payload = {'setting': setting, 'version': version}
    put(env, endpoint, token, json.dumps(payload))
    print('Autoupdate setting changed from ' + old_setting + ' to ' + setting + ' for host group ' + host_group + '(' + host_group_id + ')')


def change_host_autoupdate_setting(host, setting):
    host_id = host_lookup[host]
    endpoint = '/api/config/v1/hosts/' + host_id + '/autoupdate'
    settings_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    settings_json = settings_json_list[0]
    old_setting = settings_json.get('setting')
    version = settings_json.get('version')
    payload = {'setting': setting, 'version': version}
    put(env, endpoint, token, json.dumps(payload))
    print('Autoupdate setting changed from ' + old_setting + ' to ' + setting + ' for host ' + host + '(' + host_id + ')')


def put(env, endpoint, token, payload):
    # The host group or host id is already embedded in the endpoint
    dynatrace_api.put_object(f'{env}{endpoint}', token, payload)


def load_host_group_lookup(host_groups):
    global host_group_lookup

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST_GROUP)&to=-72h'
    # raw_params = 'entitySelector=type(HOST_GROUP)'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
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
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            display_name = inner_entities_json.get('displayName')
            if display_name in hosts:
                entity_id = inner_entities_json.get('entityId')
                host_lookup[display_name] = entity_id


if __name__ == '__main__':
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    env_name_supplied = 'Personal'  # For Safety
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    print('Updating OneAgent AutoUpdate from YAML')

    process()
