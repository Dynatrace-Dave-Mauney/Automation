from inspect import currentframe
import json
import os
import requests
import ssl
import urllib.parse

# Can be modified.  This is the key used for the tag.
tag_key = 'Queue Manager'

# Should remain constant.  This is the key for the plugin metadata used to identify MQ Queue Managers.
plugin_key = 'Queue manager'

# env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
# env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

tenant = os.environ.get(tenant_key)
token = os.environ.get(token_key)
env = f'https://{tenant}.live.dynatrace.com'


def process():
    entity_type = 'PROCESS_GROUP_INSTANCE'
    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector) + '&fields=' + urllib.parse.quote('properties.softwareTechnologies,properties.customPgMetadata,tags')
    entities_json_list = get_rest_api_json(env, endpoint, params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            properties = inner_entities_json.get('properties')
            software_technologies = properties.get('softwareTechnologies')
            custom_process_group_metadata = properties.get('customPgMetadata')
            if "IBM_MQ" in str(software_technologies) and \
                    plugin_key in str(custom_process_group_metadata) and \
                    'Queue Manager' not in str(inner_entities_json.get('tags')):
                for custom_process_group_metadata_item in custom_process_group_metadata:
                    if custom_process_group_metadata_item.get('key').get('key') == plugin_key:
                        queue_manager = custom_process_group_metadata_item.get('value')
                        print(f'Tagging {display_name} ({entity_id}) with {tag_key}: {queue_manager}')
                        post_queue_manager_tag(entity_id, queue_manager)


def post_queue_manager_tag(entity_id, queue_manager):
    entity_selector = 'entityId("' + entity_id + '")'
    params = '?entitySelector=' + urllib.parse.quote(entity_selector)
    endpoint = '/api/v2/tags' + params
    tag_body = '{"tags": [{"key": "' + tag_key + '", "value": "' + queue_manager + '"}]}'
    post(endpoint, tag_body)


def post(endpoint, payload):
    # print(endpoint, payload)
    json_data = json.loads(payload)
    formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)
    url = env + endpoint
    try:
        r = requests.post(url, payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        # print('Status Code: %d' % r.status_code)
        # print('Reason: %s' % r.reason)
        # if len(r.text) > 0:
        #     print(r.text)
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


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


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
        # next_page_key = next_page_key.replace('=', '%3D') # Ths does NOT help.  Also, equals are apparently fine in params.
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
    process()
