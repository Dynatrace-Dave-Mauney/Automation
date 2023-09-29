"""
Save Dynatrace settings specified in "include_list" to JSON files.

Token Permissions Required:
"Read settings: settings.read"
"""

import json
import os
import shutil
import urllib.parse

from inspect import currentframe

from Reuse import dynatrace_api
from Reuse import environment

friendly_function_name = 'Dynatrace Automation Tools'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Prod'
# env_name_supplied = 'NonProd'
# env_name_supplied = 'Prep'
# env_name_supplied = 'Dev'
# env_name_supplied = 'Personal'
# env_name_supplied = 'Demo'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

save_directory_path = '../../$Output/Tools/Settings20/Downloads/' + env_name

confirmation_required = True
long_file_suffix = 0

# Set to False to retain some existing saves
remove_directory_at_startup = True


def initialize():
    if remove_directory_at_startup:
        confirm('The ' + save_directory_path + ' directory will now be removed to prepare for saves.')
        remove_directory(save_directory_path)

    if not os.path.isdir(save_directory_path):
        make_directory(save_directory_path)


def remove_directory(path):
    print('remove_directory(' + path + ')')

    try:
        shutil.rmtree(path, ignore_errors=False)

    except OSError:
        print('Directory %s does not exist' % path)
    else:
        print('Removed the directory %s ' % path)


def save_settings20_objects():
    print('save_settings20_objects()')

    config_list = []

    include_schemas = ['builtin:logmonitoring.log-dpp-rules']

    endpoint = '/api/v2/settings/schemas'
    params = ''
    settings_json_list = dynatrace_api.get(env, token, endpoint, params)

    schema_ids = []
    schema_dict = {}

    for settings_json in settings_json_list:
        inner_settings_json_list = settings_json.get('items')
        for inner_settings_json in inner_settings_json_list:
            schema_id = inner_settings_json.get('schemaId')
            schema_ids.append(schema_id)
            latest_schema_version = inner_settings_json.get('latestSchemaVersion')
            schema_dict[schema_id] = latest_schema_version

    for schema_id in sorted(schema_ids):
        global long_file_suffix
        long_file_suffix = 0

        if schema_id in include_schemas:
            # display_name = inner_settings_json.get('displayName')
            # print(schema_id + ': ' + display_name)
            endpoint = '/api/v2/settings/objects'
            # params = f'schemaIds={schema_id.replace}&scopes=environment&fields=objectId,value&pageSize=500'
            raw_params = f'schemaIds={schema_id}&fields=objectId,value,scope&pageSize=500'
            params = urllib.parse.quote(raw_params, safe='/,&=')
            setting_object = dynatrace_api.get(env, token, endpoint, params)[0]
            items = setting_object.get('items')
            for item in items:
                print(item)
                if schema_id == 'builtin:logmonitoring.log-dpp-rules' and '[Built-in]' in item.get('value').get('ruleName', ''):
                    print('Skipping ' + schema_id + ' rule ' + item.get('value').get('ruleName', ''))
                else:
                    # item['scope'] = 'environment'
                    item['schemaId'] = schema_id
                    item['schemaVersion'] = schema_dict[schema_id]
                    config_list.append(item)

                    write_settings20_json(schema_id, item)


def write_settings20_json(schema_id, json_dict):
    print('write_settings20_json(' + schema_id + ',' + str(json_dict) + ')')
    dir_name = schema_id.replace(':', '.')
    save_path = save_directory_path + '/api/v2/settings/objects/' + dir_name

    object_id = json_dict.get('objectId')
    if object_id:
        write_json(save_path, object_id, json_dict)
    else:
        write_json(save_path, 'entity', json_dict)


def write_json(directory_path, filename, json_dict):
    print('write_json(' + directory_path + ',' + filename + ',' + str(json_dict) + ')')
    # print(directory_path)
    # print(filename)
    # print(json_dict)
    global long_file_suffix
    file_path = directory_path + '/' + filename
    if len(file_path) > 255:
        long_file_suffix += 1
        file_path = directory_path + '/' + str(long_file_suffix)
    if not os.path.isdir(directory_path):
        make_directory(directory_path)
    with open(file_path, 'w') as file:
        file.write(json.dumps(json_dict, indent=4, sort_keys=False))


def make_directory(path):
    print('make_directory(' + path + ')')
    try:
        os.makedirs(path)
    except OSError:
        print('Creation of the directory %s failed' % path)
        exit()
    else:
        print('Successfully created the directory %s ' % path)


def confirm(message):
    print('confirm(' + message + ')')
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            exit(get_linenumber())


def get_linenumber():
    print('get_linenumber()')
    cf = currentframe()
    return cf.f_back.f_lineno


if __name__ == '__main__':
    confirm('Save Settings 2.0 settings for ' + env_name + '?')
    initialize()
    save_settings20_objects()
