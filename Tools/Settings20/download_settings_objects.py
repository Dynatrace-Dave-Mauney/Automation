"""
Save Dynatrace settings specified in "include_list" to JSON files.

Token Permissions Required:
"Read settings: settings.read"
"""


from inspect import currentframe
import json
import os
import requests
import shutil
import urllib.parse

# Environment Details (Short Name, Tenant, Token)
# environment_details = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
# environment_details = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
environment_details = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')

env_name = environment_details[0]
tenant = os.environ.get(environment_details[1])
token = os.environ.get(environment_details[2])
env = f'https://{tenant}.live.dynatrace.com'

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


def get_rest_api_json(endpoint, params):
    print('get_rest_api_json(' + env + ', ' + token + ', ' + endpoint + ', ' + params + ')')
    full_url = env + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        print(resp.text)
        exit(get_linenumber())

    json_data = resp.json()

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json_data) is list:
        return json_data

    json_list = [json_data]
    next_page_key = json_data.get('nextPageKey')

    while next_page_key is not None:
        params = {'nextPageKey': next_page_key}
        # full_url = env + endpoint
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})

        if resp.status_code != 200:
            print('Paginated REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            print(resp.text)
            exit(get_linenumber())

        json_data = resp.json()

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def save_settings20_objects():
    print('save_settings20_objects()')

    config_list = []

    include_schemas = ['builtin:logmonitoring.log-dpp-rules']

    endpoint = '/api/v2/settings/schemas'
    params = ''
    settings_json_list = get_rest_api_json(endpoint, params)

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
            setting_object = get_rest_api_json(endpoint, params)[0]
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
