import datetime
import os
import requests
import ssl
import json
import urllib.parse

PATH = '../../$Output/Tools/Saved'

api = ''
mode = 'configs'
save_id = ''
save_content = ''


supported_environments = {
    'Prod': ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
    'Prep': ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
    'Dev': ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
    'Personal': ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN'),
}

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
        if 'get' in methods and str(endpoint).endswith('{id}'):
            line = endpoint[1:].replace('/{id}', '')
            lines.append(line)

    for line in sorted(lines):
        print(line)


def view_config(config_id, env, token):
    global api
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        url = f'{env}/api/config/v1/{api}/{config_id}'
        print(url)
        r = requests.get(url, headers=headers)
        config_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_id
            global save_content
            save_id = config_id
            save_content = config_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400:
                if "The requested configId is invalid" in r.text:
                    print('Config ID not found on this tenant')
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def list_configs(env, token):
    global api
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        url = f'{env}/api/config/v1/{api}'
        # print(url)
        r = requests.get(url, headers=headers)
        # config_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            json_response = r.json()
            values = json_response.get('values')
            lines = []
            for value in values:
                line = f'{value.get("name")}|{value.get("id")}'
                lines.append(line)
            for line in sorted(lines):
                print(line)
            # print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400:
                if "The requested configId is invalid" in r.text:
                    print('Config ID not found on this tenant')
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
            if r.status_code == 400:
                if "The requested entityId is invalid" in r.text:
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
        print(url)
        r = requests.get(url, headers=headers)
        entity_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_id
            global save_content
            save_id = entity_id
            save_content = entity_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400:
                if "The requested entityId is invalid" in r.text:
                    print('Entity ID not found on this tenant')
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def list_entity_types(env, token):
    endpoint = '/api/v2/entityTypes'
    params = ''
    entities_json_list = get_rest_api_json(env, token, endpoint, params)

    print('id' + '|' + 'name')

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('types')
        for inner_entities_json in inner_entities_json_list:
            # print(inner_entities_json)
            entity_type = inner_entities_json.get('type')
            display_name = inner_entities_json.get('displayName')
            print(entity_type + '|' + display_name)


def list_entities_of_type(env, token, entity_type):
    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector)
    entities_json_list = get_rest_api_json(env, token, endpoint, params)

    lines = []

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            line = f'{display_name}|{entity_id}'
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


def list_schemas(env, token):
    endpoint = '/api/v2/settings/schemas'
    params = ''
    settings_json_list = get_rest_api_json(env, token, endpoint, params)

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
        print(schema_id)


def list_objects_at_environment_scope(env, token):
    endpoint = '/api/v2/settings/objects'
    raw_params = 'scopes=environment&fields=schemaId,value&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object = get_rest_api_json(env, token, endpoint, params)[0]
    items = settings_object.get('items')
    for item in items:
        schema_id = item.get('schemaId')
        value = str(item.get('value'))
        value = value.replace('{', '')
        value = value.replace('}', '')
        value = value.replace("'", "")
        print(schema_id + ': ' + value)


def list_objects_of_schema(env, token, schema_id):
    # print(f'list_objects_of_schema: {schema_id}')
    endpoint = f'/api/v2/settings/objects'
    raw_params = f'schemaIds={schema_id}&fields=scope,value&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object = get_rest_api_json(env, token, endpoint, params)[0]
    # print(settings_object)

    items = settings_object.get('items')
    for item in items:
        scope = item.get('scope')
        value = str(item.get('value'))
        value = value.replace('{', '')
        value = value.replace('}', '')
        value = value.replace("'", "")
        print(f'scope: {scope}, {value}')


def list_metrics(env, token):
    endpoint = '/api/v2/metrics'
    # raw_params = 'pageSize=500&fields=+created'
    raw_params = 'pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    metrics_json_list = get_rest_api_json(env, token, endpoint, params)
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
            if r.status_code == 400:
                if "The requested metricId is invalid" in r.text:
                    print('Entity ID not found on this tenant')
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
            if r.status_code == 400:
                if "The requested metricId is invalid" in r.text:
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
            if r.status_code == 400:
                if "The requested eventId is invalid" in r.text:
                    print('Event ID not found on this tenant')
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def list_events(env, token):
    endpoint = '/api/v2/events'
    page_size = 1000
    from_time = 'now-24h'
    params = f'pageSize={page_size}&from={from_time}'
    events_json_list = get_rest_api_json(env, token, endpoint, params)

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
            print(f'{event_id}|{event_type}|{event_title}|{start_date_time}|{end_date_time}|{formatted_duration}')


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


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

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
        # print(f'next_page_key: {next_page_key}')
        params = {'nextPageKey': next_page_key}
        full_url = url + endpoint
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
        # print(resp.url)

        if resp.status_code != 200:
            print('Paginated REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            exit(1)

        json_data = resp.json()
        # print(json_data)

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def convert_epoch_in_milliseconds_to_local(epoch):
    if epoch == -1:
        return None
    else:
        return datetime.datetime.fromtimestamp(epoch / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def save(path, file, content):
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + "/" + file, "w", encoding='utf8') as text_file:
        text_file.write("%s" % content)


def change_environment(new_env):
    if new_env not in supported_environments:
        print('Invalid Environment Name...')
        return new_env, 'INVALID', 'NA'

    return supported_environments.get(new_env)


def run():
    global api
    global mode
    global save_id
    global save_content

    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

    print(f'Environment Name: {env_name}')
    print(f'Environment:      {env}')
    print(f'Token:            {masked_token}')

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
                    save_path = f'{PATH}/Config/{api}/{env_name}'
                else:
                    save_path = f'{PATH}/{mode.capitalize()}/{env_name}'
                save(save_path, save_id + '.json', save_content)
                print(f'Saved {save_path}/{save_id}.json')
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
                list_schemas(env, token)
                continue
            else:
                print('list schemas only applies to "settings20" mode.')
                continue

        if input_string.upper() == 'L':
            if mode == 'configs':
                if api == '':
                    print('No API set yet.  Use the "a" command to set an API. Use the "la" command to list APIs for copy/paste convenience.')
                    continue
                else:
                    list_configs(env, token)
                    continue
            else:
                if mode == 'events':
                    list_events(env, token)
                    continue
                else:
                    if mode == 'metrics':
                        list_metrics(env, token)
                        continue
                    else:
                        if mode == 'settings20':
                            list_objects_at_environment_scope(env, token)
                            continue
                        else:
                            if mode == 'entities':
                                list_entity_types(env, token)
                                continue
                            else:
                                print('Only supported for "configs", "entities" and "events" modes.')
                                continue

        if input_string.upper().startswith('L '):
            argument = input_string.split(' ')[1]
            if mode == 'entities':
                list_entities_of_type(env, token, argument)
                continue
            else:
                if mode == 'settings20':
                    list_objects_of_schema(env, token, argument)
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
            print(f'Token:            {masked_token}')
            continue

        if input_string.upper().startswith('E '):
            new_env = input_string.split(' ')[1]

            if new_env not in supported_environments:
                print('Invalid Environment Name...')
                continue

            env_name, tenant_key, token_key = change_environment(new_env)
            tenant = os.environ.get(tenant_key)
            token = os.environ.get(token_key)
            env = f'https://{tenant}.live.dynatrace.com'

            masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

            print(f'Environment Name: {env_name}')
            print(f'Environment:      {env}')
            print(f'Token:            {masked_token}')

            continue

        if mode == 'configs' and api == '':
            print('Please use the "a <api>" command to set an API')
            print('Hint: use the "la" command to list APIs and copy one from the list')
            continue

        if ' ' in input_string.rstrip().lstrip():
            print('Invalid command or config id. (Embedded space detected).')
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
    print('')
    print(f'Enter "e Prod|Perf|Dev|Personal" to change the environment. "e" without a parameter shows the current environment.')
    print(f'Enter "m configs|entities|entities_v1|events|metrics|settings20" to change the mode. "m" without a parameter shows the current mode.')
    print(f'Enter "a <api>" to set/change an api (in configs mode). "a" without a parameter shows the current api.')
    print(f'Enter "l to list items')
    print(f'Enter "la" to list apis (in configs mode)')
    print(f'Enter "mq" to query a metric selector (in metrics mode)')
    print(f'Enter just an ID to get the JSON')
    print(f'Enter "s" to save JSON just viewed')
    print(f'Enter "q" to quit')
    print(f'Enter "h" to view this help message')
    print('')


if __name__ == '__main__':
    run()
