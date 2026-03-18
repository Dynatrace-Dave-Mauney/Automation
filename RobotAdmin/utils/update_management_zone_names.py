import copy
import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

friendly_function_name = 'Dynatrace Automation'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Prod'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)


def change_names():
    endpoint = '/api/config/v1/managementZones'

    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    config_json = r.json()
    config_list = config_json.get('values')
    for config in config_list:
        object_id = copy.deepcopy(config.get('id'))
        name = copy.deepcopy(config.get('name'))
        if 'HG: ' in name:
            new_name = name.replace('HG: ', 'HG:')
            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{object_id}', token)
            config_object = r.json()
            config_object['name'] = new_name
            print(new_name)
            dynatrace_api.put_object(f'{env}{endpoint}/{object_id}', token, json.dumps(config_object))


def process():
    # For when everything is commented out below...
    pass

    enhancement_type = 'NameChange'

    if enhancement_type == 'NameChange':
        change_names()
    else:
        print('Specify a supported enhancement type and run again')


if __name__ == '__main__':
    process()
