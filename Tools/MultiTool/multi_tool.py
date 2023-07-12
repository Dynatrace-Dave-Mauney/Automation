import datetime
import os
import re
import requests
import ssl
import json
import urllib.parse
from inspect import currentframe
from requests import Response

from Reuse import environment
from Reuse import dynatrace_api

PATH = '../../$Output/Tools/MultiTool/Saved'

api = ''
mode = 'configs'
save_id = ''
save_content = ''


# supported_environments = {
#     'Prod': ('PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
#     'NonProd': ('NONPROD_TENANT', 'ROBOT_ADMIN_NONPROD_TOKEN'),
#     # 'Prep': ('PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
#     # 'Dev': ('DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
#     'Personal': ('PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN'),
#     'FreeTrial1': ('FREETRIAL1_TENANT', 'ROBOT_ADMIN_FREETRIAL1_TOKEN'),
# }

# supported_environments = ['Prod', 'NonProd', 'Prep', 'Dev', 'Personal', 'FreeTrial1']
supported_environments = ['Prod', 'NonProd']

supported_modes = ['configs', 'entities', 'entities_v1', 'events', 'metrics', 'settings20']


def list_config_endpoints():
    f = open('config_v1_spec3.json', )
    data = json.load(f)

    paths = data.get('paths')
    endpoints = list(paths.keys())

    lines = []

    for endpoint in endpoints:
        endpoint_dict = paths.get(endpoint)
        methods = list(endpoint_dict.keys())
        # if 'get' in methods and str(endpoint).endswith('{id}'):
        #     line = endpoint[1:].replace('/{id}', '')
        #     lines.append(line)
        if 'get' in methods and '{' not in str(endpoint):
            line = endpoint[1:]
            lines.append(line)

    for line in sorted(lines):
        print(line)


def view_config(config_id, env, token):
    global api
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        url = f'{env}/api/config/v1/{api}/{config_id}'
        # print(url)
        r = requests.get(url, headers=headers)
        config_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_id
            global save_content
            save_id = config_id
            save_content = config_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 404:
                print('Config ID not found on this tenant')
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def get_config(config_id, env, token):
    global api
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        url = f'{env}/api/config/v1/{api}/{config_id}'
        # print(url)
        r = requests.get(url, headers=headers)
        # config_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            return r.json()
        else:
            if r.status_code == 404:
                return None
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def list_configs(env, token, filtering):
    global api
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        url = f'{env}/api/config/v1/{api}'
        print(url)
        r = requests.get(url, headers=headers)
        # config_content = json.dumps(r.json(), indent=4)

        if r.status_code == 200:
            json_response = r.json()

            if api == 'dashboards':
                key = 'dashboards'
            else:
                if api == 'extensions':
                    key = 'extensions'
                else:
                    if api == 'technologies':
                        key = 'technologies'
                    else:
                        key = 'values'

            # For the endpoints that do not support lists or have not been added to the list above yet
            values = json_response

            if key in str(json_response):
                values = json_response.get(key)

            lines = []

            if isinstance(values, list):
                for value in values:
                    if isinstance(value, dict):
                        entity_name = value.get('name')
                        entity_id = value.get('id')
                        if entity_name and entity_id:
                            if api == 'dashboards':
                                owner = value.get('owner')
                                line = f'{entity_name}|{entity_id}|{owner}'
                            else:
                                line = f'{entity_name}|{entity_id}'
                            if not filtering or filtering in line:
                                lines.append(line)
                        else:
                            line = str(value)
                            if not filtering or filtering in line:
                                lines.append(line)
                    else:
                        line = str(value)
                        if not filtering or filtering in line:
                            lines.append(line)
            else:
                line = str(values)
                if not filtering or filtering in line:
                    lines.append(line)

            for line in sorted(lines):
                print(line)
        else:
            if r.status_code == 404:
                if "HTTP 404 Not Found" in r.text:
                    print(f'No entries for API {api} found on this tenant')
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def view_entity(entity_id, env, token):
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        r = requests.get(env + '/api/v2/entities/' + entity_id, headers=headers)
        entity_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_id
            global save_content
            save_id = entity_id
            save_content = entity_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400 and "The requested entityId is invalid" in r.text:
                print('Entity ID not found on this tenant')
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def view_entity_v1(entity_id, env, token):
    entity_endpoints = {
        'APPLICATION': 'entity/applications',
        # 'CUSTOM_DEVICE': 'entity/infrastructure/custom',
        'HOST': 'entity/infrastructure/hosts',
        'HTTP_CHECK': 'synthetic/monitors',
        'PROCESS_GROUP': 'entity/infrastructure/process-groups',
        'PROCESS_GROUP_INSTANCE': 'entity/infrastructure/processes',
        'SERVICE': 'entity/services',
        'SYNTHETIC_TEST': 'synthetic/monitors',
    }

    headers = {'Authorization': 'Api-Token ' + token}

    entity_type = entity_id.split('-')[0]

    entity_endpoint = entity_endpoints.get(entity_type)

    if not entity_endpoint:
        print(f'Entity type not supported: {entity_type}')
        print(f'Supported Entities: {entity_endpoints.keys()}')
        return

    try:
        url = f'{env}/api/v1/{entity_endpoint}/{entity_id}'
        # print(url)
        r = requests.get(url, headers=headers)
        entity_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_id
            global save_content
            save_id = entity_id
            save_content = entity_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 404 and "The given entity id is not assigned to an entity" in r.text:
                print('Entity ID not found on this tenant')
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def list_entity_types(env, token, filtering):
    endpoint = '/api/v2/entityTypes'
    params = ''
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)

    print('id' + '|' + 'name')

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('types')
        for inner_entities_json in inner_entities_json_list:
            # print(inner_entities_json)
            entity_type = inner_entities_json.get('type')
            display_name = inner_entities_json.get('displayName')
            line = f'{entity_type}|{display_name}'
            if not filtering or filtering in line:
                print(line)


def list_entities_of_type(env, token, entity_type, filtering):
    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector)
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)

    lines = []

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            line = f'{display_name}|{entity_id}'
            if not filtering or filtering in line:
                lines.append(line)

    for line in sorted(lines):
        print(line)


def view_object(object_id, env, token):
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        r = requests.get(env + '/api/v2/settings/objects/' + object_id, headers=headers)
        object_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_id
            global save_content
            save_id = object_id
            save_content = object_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400 and "Could not decode" in r.text:
                print('Could not decode the Object ID')
            else:
                if r.status_code == 404 and "not found" in r.text:
                    print('Object ID not found on this tenant')
                else:
                    print('Status Code: %d' % r.status_code)
                    print('Reason: %s' % r.reason)
                    if len(r.text) > 0:
                        print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def list_schemas(env, token, filtering):
    endpoint = '/api/v2/settings/schemas'
    params = ''
    settings_json_list = dynatrace_api.get(env, token, endpoint, params)

    schema_ids = []
    schema_dict = {}

    for settings_json in settings_json_list:
        inner_settings_json_list = settings_json.get('items')
        for inner_settings_json in inner_settings_json_list:
            schema_id = inner_settings_json.get('schemaId')
            if not filtering or filtering in schema_id:
                schema_ids.append(schema_id)
                latest_schema_version = inner_settings_json.get('latestSchemaVersion')
                schema_dict[schema_id] = latest_schema_version

    for schema_id in sorted(schema_ids):
        print(schema_id)


def list_objects_at_environment_scope(env, token, filtering):
    endpoint = '/api/v2/settings/objects'
    raw_params = 'scopes=environment&fields=schemaId,value&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object_list = dynatrace_api.get(env, token, endpoint, params)
    for settings_object in settings_object_list:
        items = settings_object.get('items')
        for item in items:
            schema_id = item.get('schemaId')
            value = str(item.get('value'))
            value = value.replace('{', '')
            value = value.replace('}', '')
            value = value.replace("'", "")
            line = f'{schema_id}:{value}'
            if not filtering or filtering in line:
                print(line)


def list_objects_of_schema(env, token, schema_id, filtering):
    # print(f'list_objects_of_schema: {schema_id}')
    endpoint = f'/api/v2/settings/objects'
    raw_params = f'schemaIds={schema_id}&fields=scope,objectId,value&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object = dynatrace_api.get(env, token, endpoint, params)[0]
    error_code = settings_object.get('error', {}).get('code', None)
    if error_code:
        if error_code == 404:
            print('Schema type not found')
        else:
            print('Something went wrong when getting the schema')
    else:
        items = settings_object.get('items')
        for item in items:
            print(item)
            scope = item.get('scope')
            object_id = item.get('objectId')
            update_token = item.get('updateToken')
            value = str(item.get('value'))
            value = value.replace('{', '')
            value = value.replace('}', '')
            value = value.replace("'", "")
            line = f'{object_id}, {update_token}, scope: {scope}, {value}'
            # if not filtering or filtering in line:
            #     print(line)


def list_metrics(env, token, filtering):
    endpoint = '/api/v2/metrics'
    # raw_params = 'pageSize=500&fields=+created'
    raw_params = 'pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    metrics_json_list = dynatrace_api.get(env, token, endpoint, params)
    # print('metric_id' + '|' + 'displayName' + '|' + 'created')
    print('metric_id' + '|' + 'displayName')

    lines = []

    for metrics_json in metrics_json_list:
        inner_metrics_json_list = metrics_json.get('metrics')
        for inner_metrics_json in inner_metrics_json_list:
            metric_id = inner_metrics_json.get('metricId')
            display_name = inner_metrics_json.get('displayName')
            # created = inner_metrics_json.get('created')
            # print(metric_id + '|' + display_name + '|' + str(created))
            line = f'{metric_id}|{display_name}'
            if not filtering or filtering in metric_id:
                lines.append(line)

    for line in sorted(lines):
        print(line)


def view_metric(metric_id, env, token):
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        r = requests.get(env + '/api/v2/metrics/' + metric_id, headers=headers)
        metric_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_id
            global save_content
            save_id = metric_id
            save_content = metric_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400 and "The requested metricId is invalid" in r.text:
                print('Metric ID invalid')
            else:
                if r.status_code == 404 and "No metric found using the Metric Id" in r.text:
                    print('Metric ID not found on this tenant')
                else:
                    print('Status Code: %d' % r.status_code)
                    print('Reason: %s' % r.reason)
                    if len(r.text) > 0:
                        print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def view_metric_query(metric_selector, env, token):
    endpoint = '/api/v2/metrics/query'
    try:
        full_url = env + endpoint
        raw_params = f'metricSelector={metric_selector}'
        params = urllib.parse.quote(raw_params, safe='/,&=')
        r = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
        metric_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_id
            global save_content
            save_id = metric_selector
            save_content = metric_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400 and "The requested metricId is invalid" in r.text:
                print('Metric ID invalid')
            else:
                if r.status_code == 404 and "No metric found using the Metric Id" in r.text:
                    print('Metric ID not found on this tenant')
                else:
                    print('Status Code: %d' % r.status_code)
                    print('Reason: %s' % r.reason)
                    if len(r.text) > 0:
                        print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def view_event(event_id, env, token):
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        r = requests.get(env + '/api/v2/events/' + event_id, headers=headers)
        event_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_id
            global save_content
            save_id = event_id
            save_content = event_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400 and "Unable to find event with id" in r.text:
                print('Event ID not found on this tenant')
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def list_events(env, token, filtering):
    endpoint = '/api/v2/events'
    page_size = 1000
    from_time = 'now-24h'
    params = f'pageSize={page_size}&from={from_time}'
    events_json_list = dynatrace_api.get(env, token, endpoint, params)

    print('Events')
    print('eventId|eventType|title|startTime|endTime|duration (D:HH:MM:SS.MMM')

    for events_json in events_json_list:
        inner_events_json_list = events_json.get('events')
        for inner_events_json in inner_events_json_list:
            event_id = inner_events_json.get('eventId')
            event_type = inner_events_json.get('eventType')
            event_title = inner_events_json.get('title')
            start_time = inner_events_json.get('startTime')
            end_time = inner_events_json.get('endTime')
            start_date_time = convert_epoch_in_milliseconds_to_local(start_time)
            end_date_time = convert_epoch_in_milliseconds_to_local(end_time)
            formatted_duration = format_time_duration(start_time, end_time)
            line = f'{event_id}|{event_type}|{event_title}|{start_date_time}|{end_date_time}|{formatted_duration}'
            if not filtering or filtering in line:
                print(line)


def format_time_duration(start_time, end_time):
    if end_time == -1:
        return 'ONGOING'
    else:
        duration = (end_time - start_time) // 1000
        millis = str(duration)[-3:]
        days = hours = minutes = 0
        if duration > 86400:
            days = duration // 86400
            duration -= days * 86400
        if duration > 3600:
            hours = duration // 3600
            duration -= hours * 3600
        if duration > 60:
            minutes = duration // 60
            duration -= minutes * 60
        formatted_time_duration = f'{days}:{hours:02d}:{minutes:02d}:{duration:02d}.{millis}'
        return formatted_time_duration


def post(env, token, endpoint: str, payload: str) -> Response:
    # In general, avoid post in favor of put so "fixed ids" can be used
    json_data = json.loads(payload)
    # Remove id proactively
    if json_data.get('id'):
        json_data.pop('id')
    formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)
    url = env + endpoint
    try:
        r: Response = requests.post(url, formatted_payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        if r.status_code == 201:
            config_id = r.json().get('id')
            config_name = r.json().get('name')
            print(f'Created new configuration: "{config_name}" ({config_id}) at endpoint "{endpoint}"')
        else:
            error_filename = '$post_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(formatted_payload)
                name = json_data.get('name')
                if name:
                    print('Name: ' + name)
                print('Error in "post(env, token, endpoint, payload)" method')
                print('See ' + error_filename + ' for more details')
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def put(env, token, endpoint: str, config_id, payload: str) -> Response:
    json_data = json.loads(payload)
    formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)

    url = env + endpoint + '/' + config_id
    try:
        r: Response = requests.put(url, formatted_payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        if r.status_code == 201:
            config_name = json_data.get('name')
            print(f'Created new configuration: "{config_name}" ({config_id}) at endpoint "{endpoint}"')
        else:
            if r.status_code == 204:
                print(f'Updated configuration: "{config_id}" at endpoint "{endpoint}"')
            else:
                error_filename = '$put_error_payload.json'
                with open(error_filename, 'w') as file:
                    file.write(formatted_payload)
                    name = json_data.get('name')
                    if name:
                        print('Name: ' + name)
                    print('Error in "put(env, token, endpoint, config_id, payload)" method')
                    print('See ' + error_filename + ' for more details')
                    print('Status Code: %d' % r.status_code)
                    print('Reason: %s' % r.reason)
                    if len(r.text) > 0:
                        print(r.text)
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def delete(env, token, endpoint: str, config_id) -> Response:
    url = env + endpoint + '/' + config_id
    try:
        r: Response = requests.delete(url, headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        if r.status_code == 204:
            print('Config object was deleted')
        else:
            if r.status_code == 404:
                print('Config object with specified Id does not exist.')
            else:
                if r.status_code not in [200, 201, 204]:
                    print('Error in "delete(env, token, endpoint, config_id)" method')
                    print('Status Code: %d' % r.status_code)
                    print('Reason: %s' % r.reason)
                    if len(r.text) > 0:
                        print(r.text)
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def convert_epoch_in_milliseconds_to_local(epoch):
    if epoch == -1:
        return None
    else:
        return datetime.datetime.fromtimestamp(epoch / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def save(path, file, content):
    clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", file)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + "/" + clean_filename, "w", encoding='utf8') as text_file:
        text_file.write("%s" % content)
        print(f'Saved {path}/{clean_filename}')


def change_environment(new_env):
    if new_env not in supported_environments:
        print('Invalid Environment Name...')
        return new_env, 'INVALID', 'NA'

    friendly_function_name = 'Dynatrace Automation Tools'
    return environment.get_environment_for_function(new_env, friendly_function_name)
    # return environment.get_environment(new_env)



def run():
    global api
    global mode
    global save_id
    global save_content

    # Set Environment
    friendly_function_name = 'Dynatrace Automation Tools'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    print_help()

    while True:
        message = '> '
        input_string = input('%s' % message).rstrip().lstrip()

        if input_string.upper() == 'Q':
            print('Exiting per user request')
            exit()

        if input_string.upper() == 'H':
            print_help()
            continue

        if input_string.upper() == 'S':
            global api
            if save_id == '':
                print('There is nothing to save yet')
                continue
            else:
                if mode == 'configs':
                    save_path = f'{PATH}/{env_name}/Config/{api}'
                else:
                    save_path = f'{PATH}/{env_name}/{mode.capitalize()}'
                save(save_path, save_id + '.json', save_content)
                continue

        if input_string.upper() == 'LA':
            if mode == 'configs':
                list_config_endpoints()
                continue
            else:
                print('list apis only applies to "configs" mode.')
                continue

        if input_string.upper() == 'LS':
            if mode == 'settings20':
                list_schemas(env, token, None)
                continue
            else:
                print('list schemas only applies to "settings20" mode.')
                continue

        if input_string.upper() == 'L' or input_string.upper().startswith('LF '):
            filtering = None
            if input_string.upper().startswith('LF'):
                filtering = input_string.split(' ')[1]
            if mode == 'configs':
                if api == '':
                    print('No API set yet.  Use the "a" command to set an API. Use the "la" command to list APIs for copy/paste convenience.')
                    continue
                else:
                    list_configs(env, token, filtering)
                    continue
            else:
                if mode == 'events':
                    list_events(env, token, filtering)
                    continue
                else:
                    if mode == 'metrics':
                        list_metrics(env, token, filtering)
                        continue
                    else:
                        if mode == 'settings20':
                            list_objects_at_environment_scope(env, token, filtering)
                            continue
                        else:
                            if mode == 'entities':
                                list_entity_types(env, token, filtering)
                                continue
                            else:
                                print('Only supported for "configs", "entities" and "events" modes.')
                                continue

        if input_string.upper().startswith('L '):
            argument = input_string.split(' ')[1]
            if mode == 'entities':
                list_entities_of_type(env, token, argument, None)
                continue
            else:
                if mode == 'settings20':
                    list_objects_of_schema(env, token, argument, None)
                    continue
                else:
                    print('Only supported for "entities" and "settings20" modes.')
                    continue

        if input_string.upper() == 'A':
            if api == '':
                print(f'API is currently not set')
            else:
                print(f'API is currently set to {api}')
            continue

        if input_string.upper().startswith('A '):
            api = input_string.split(' ')[1]
            print(f'API set to {api}')
            continue

        if input_string.upper() == 'M':
            print(f'Mode is currently set to {mode}')
            continue

        if input_string.upper().startswith('M '):
            new_mode = input_string.split(' ')[1]
            if new_mode in supported_modes:
                mode = new_mode
                print(f'Mode is now {mode}')
                continue
            else:
                print('Invalid mode.  Enter one of "configs|entities|entities_v1|events|metrics|settings20"')
                continue

        if input_string.upper().startswith('MQ '):
            if mode == 'metrics':
                metric_query = input_string.split(' ')[1]
                view_metric_query(metric_query, env, token)
                continue
            else:
                print('metric query only applies to "metrics" mode.')
                continue

        if input_string.upper() == 'E':
            print(f'Environment is currently set to:')
            print(f'Environment Name: {env_name}')
            print(f'Environment:      {env}')
            continue

        if input_string.upper().startswith('E '):
            new_env = input_string.split(' ')[1]

            env_name, env, token = change_environment(new_env)

            continue

        if mode == 'configs' and api == '':
            print('Please use the "a <api>" command to set an API')
            print('Hint: use the "la" command to list APIs and copy one from the list')
            continue

        if input_string.upper().startswith('POST '):
            if mode != 'configs' or api == '':
                print('Must be in configs mode with an API set in order to perform a post!')
                print(f'Current mode:  {mode}')
                print(f'Current API:  {api}')
            else:
                post_file_name = input_string[5:]
                if os.path.isfile(post_file_name):
                    endpoint = f'/api/config/v1/{api}'
                    with open(post_file_name, 'r', encoding='utf-8') as file:
                        payload = file.read()
                        post(env, token, endpoint, payload)
                else:
                    print(f'Invalid file path: {post_file_name}')
            continue

        if input_string.upper().startswith('PUT '):
            if mode != 'configs' or api == '':
                print('Must be in configs mode with an API set in order to perform a put!')
                print(f'Current mode:  {mode}')
                print(f'Current API:  {api}')
            else:
                put_file_name = input_string[4:]
                if os.path.isfile(put_file_name):
                    endpoint = f'/api/config/v1/{api}'
                    with open(put_file_name, 'r', encoding='utf-8') as file:
                        payload = file.read()
                        json_data = json.loads(payload)
                        config_id = json_data.get('id')
                        if not config_id:
                            print('Unable to extract id from payload:')
                            print(json_data)
                        config_object = get_config(config_id, env, token)
                        if config_object:
                            save_path = f'{PATH}/{env_name}/PUT/Backup/Config/{api}'
                            save(save_path, config_id + '.json', save_content)
                            print(f'Existing configuration saved to {save_path}/{config_id}.json')
                        put(env, token, endpoint, config_id, payload)
                else:
                    print(f'Invalid file path: {put_file_name}')
            continue

        if input_string.upper().startswith('DELETE '):
            if mode != 'configs' or api == '':
                print('Must be in configs mode with an API set in order to perform a delete!')
                print(f'Current mode:  {mode}')
                print(f'Current API:  {api}')
            else:
                config_id = input_string[7:]
                save_path = f'{PATH}/{env_name}/DELETE/Backup/Config/{api}'
                save(save_path, config_id + '.json', save_content)
                print(f'Existing configuration saved to {save_path}/{config_id}.json')
                endpoint = f'/api/config/v1/{api}'
                delete(env, token, endpoint, config_id)
            continue

        if ' ' in input_string.rstrip().lstrip():
            print('Invalid command or config id. (Embedded space detected).')
            continue

        if input_string.rstrip().lstrip() == '':
            print('Empty command ignored')
            continue

        if mode == 'configs':
            view_config(input_string, env, token)
        else:
            if mode == 'entities':
                view_entity(input_string, env, token)
            else:
                if mode == 'entities_v1':
                    view_entity_v1(input_string, env, token)
                else:
                    if mode == 'events':
                        view_event(input_string, env, token)
                    else:
                        if mode == 'metrics':
                            view_metric(input_string, env, token)
                        else:
                            if mode == 'settings20':
                                view_object(input_string, env, token)
                            else:
                                print('Mode not yet supported!')


def print_help():
    # supported_environment_options = str(supported_environments.keys()).replace("dict_keys(['", '').replace("', '", '|').replace("'])", '')
    supported_environment_options = str(supported_environments).replace("['", '').replace("', '", '|').replace("']", '')
    print('')
    print(f'Enter "e {supported_environment_options}" to change the environment. "e" without a parameter shows the current environment.')
    print(f'Enter "m configs|entities|entities_v1|events|metrics|settings20" to change the mode. "m" without a parameter shows the current mode.')
    print(f'Enter "a <api>" to set/change an api (in configs mode). "a" without a parameter shows the current api.')
    print(f'Enter "l to list items')
    print(f'Enter "la" to list apis (in configs mode)')
    print(f'Enter "lf <filtering string>" to list items and filtering for content (supports a single string with no spaces as the filtering)')
    print(f'Enter "mq" to query a metric selector (in metrics mode)')
    print(f'Enter "post" to post JSON from a file path specified to a config endpoint (in configs mode)')
    print(f'Enter "put" to put JSON from a file path specified to a config endpoint (in configs mode)')
    print(f'Enter "delete <id>" to delete the specified id from a config endpoint (in configs mode)')
    print(f'Enter just an ID to get the JSON')
    print(f'Enter "s" to save JSON just viewed')
    print(f'Enter "q" to quit')
    print(f'Enter "h" to view this help message')
    print('')


if __name__ == '__main__':
    run()
