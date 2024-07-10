"""

PUT SLO dashboards based on a template after changing the necessary fields.

Supported dashboard_type values: 'HTTP_CHECK', 'SYNTHETIC_TEST', 'SERVICE' and 'HOST'

"""

import base64
import json
import urllib.parse

from Reuse import directories_and_files
from Reuse import dynatrace_api
from Reuse import environment

allow_rewrites = True


def load_lookups(target_env_name, target_env, target_token):
    # if target_env_name not in lookups:
    # print('Loading lookups...')
    lookups = {target_env_name: {'management_zones': {}, 'slos': {}}}
    lookups = load_lookup_management_zones(lookups, target_env_name, target_env, target_token)
    lookups = load_lookup_slos(lookups, target_env_name, target_env, target_token)

    return lookups


def load_lookup_management_zones(lookups, target_env_name,  target_env, target_token):
    endpoint = '/api/config/v1/managementZones'
    url = target_env + endpoint
    management_zones_json_list = dynatrace_api.get_json_list_with_pagination(url, target_token)
    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        for inner_management_zones_json in inner_management_zones_json_list:
            management_zone_id = inner_management_zones_json.get('id')
            management_zone_name = inner_management_zones_json.get('name')
            lookups[target_env_name]['management_zones'][management_zone_name] = management_zone_id

    return lookups


def load_lookup_slos(lookups, target_env_name, target_env, target_token):
    endpoint = '/api/v2/settings/objects'
    raw_params = 'schemaIds=builtin:monitoring.slo'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    url = target_env + endpoint
    slos_json_list = dynatrace_api.get_json_list_with_pagination(url, target_token, params=params)

    for slos_json in slos_json_list:
        inner_slos_json_list = slos_json.get('items')
        for inner_slos_json in inner_slos_json_list:
            slo_id = inner_slos_json.get('objectId')
            slo_name = inner_slos_json.get('value').get('name')
            if '- Synthetic Availability' in slo_name or '- Service Errors' in slo_name or '- Service Performance' in slo_name or '- Host Availability' in slo_name:
                lookups[target_env_name]['slos'][slo_name] = slo_id

    return lookups


def get_management_zone_id(lookups, target_env_name, management_zone_name):
    try:
        management_zone_id = lookups[target_env_name]['management_zones'][management_zone_name]
        return management_zone_id
    except KeyError:
        print(f'Management Zone ID lookup failed for {management_zone_name} in environment {target_env_name}')
        return None


def get_slo_id(lookups, target_env_name, slo_name):
    try:
        slo_id = lookups[target_env_name]['slos'][slo_name]
        return slo_id
    except KeyError:
        print(f'SLO ID lookup failed for {slo_name} in environment {target_env_name}')
        # DEBUG
        # traceback.print_exc()
        # raise KeyError
        return None


def object_id_to_entity_id(object_id):
    # Add double equals to force pad regardless of remainder
    # https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding/49459036#49459036
    decoded_object_id_bytes = base64.urlsafe_b64decode(object_id + '==')

    # Remove the first 13 bytes and remove the bytes indicator while converting to a string
    schema_id = str(decoded_object_id_bytes[12:]).replace("b'", "")

    # Truncate after the first byte delimiter that indicates the end of the schema id
    entity_id = schema_id[:schema_id.find('\\')]

    return entity_id


def load_http_check_availability_slo_dashboard_template():
    file_path = 'standard_http_slo_dashboard_template.json'
    with open(file_path, 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def load_browser_availability_slo_dashboard_template():
    file_path = 'standard_browser_slo_dashboard_template.json'
    with open(file_path, 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def load_service_slo_dashboard_template():
    file_path = 'standard_service_slo_dashboard_template.json'
    with open(file_path, 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def load_host_availability_slo_dashboard_template():
    file_path = 'standard_host_slo_dashboard_template.json'
    with open(file_path, 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def put_synthetic_slo_dashboard(env_name, env, token, management_zone_name, dashboard_type, lookups):

    dashboard_id = get_dashboard_id(management_zone_name, dashboard_type)

    management_zone_id = get_management_zone_id(lookups, env_name, management_zone_name)
    if not management_zone_id:
        print(f'Cannot build Synthetic SLO Dashboard: Management zone not found for "{management_zone_name}"')
        return

    management_zone_name_clean = directories_and_files.get_clean_file_name(management_zone_name, '_').replace(' ', '')

    if dashboard_type == 'HTTP_CHECK':
        synthetic_slo_dashboard = load_http_check_availability_slo_dashboard_template()
        dashboard_name = f'{management_zone_name} Synthetic HTTP SLOs'
        metric_id = f'func:slo.{management_zone_name_clean.lower().replace("-", "_")}_synthetic_availability'
        metrics_string = f'METRICS=true;LEGEND=true;PROBLEMS=true;decimals=10;customTitle={management_zone_name} - Synthetic Availability (HTTP);'
        slo_name = f'{management_zone_name} - Synthetic Availability (HTTP)'
    else:
        synthetic_slo_dashboard = load_browser_availability_slo_dashboard_template()
        dashboard_name = f'{management_zone_name} Synthetic Browser SLOs'
        metric_id = f'func:slo.{management_zone_name_clean.lower().replace("-", "_")}_synthetic_browser_availability'
        metrics_string = f'METRICS=true;LEGEND=true;PROBLEMS=true;decimals=10;customTitle={management_zone_name} - Synthetic Availability (Browser);'
        slo_name = f'{management_zone_name} - Synthetic Availability (Browser)'

    slo_id = get_slo_id(lookups, env_name, slo_name)
    if not slo_id:
        print(f'Cannot build Synthetic SLO Dashboard: SLO id not found for SLO name "{slo_name}"')
        return

    # TODO: This is a hack to get the entity id from an update token to add as dashboard tile reference
    endpoint = '/api/v2/settings/objects'
    url = env + endpoint + '/' + slo_id
    # settings_object = get_by_object_id(env, token, endpoint, slo_id)
    settings_object = dynatrace_api.get_without_pagination(url, token).json()

    update_token = settings_object.get('updateToken')

    assigned_entity = object_id_to_entity_id(update_token)

    synthetic_slo_dashboard['id'] = dashboard_id
    synthetic_slo_dashboard['dashboardMetadata']['name'] = dashboard_name
    synthetic_slo_dashboard['dashboardMetadata']['owner'] = 'Admin'
    synthetic_slo_dashboard['dashboardMetadata']['dashboardFilter']['managementZone']['id'] = management_zone_id
    synthetic_slo_dashboard['dashboardMetadata']['dashboardFilter']['managementZone']['name'] = management_zone_name
    if synthetic_slo_dashboard.get('dashboardMetadata').get('popularity', None):
        synthetic_slo_dashboard['dashboardMetadata'].pop('popularity')

    tiles = synthetic_slo_dashboard['tiles']

    for tile in tiles:
        if tile['tileType'] == 'SLO':
            tile['assignedEntities'] = [assigned_entity]
            tile['metric'] = metrics_string
        else:
            if tile['tileType'] == 'DATA_EXPLORER' and tile['name'] == '':
                tile['queries'][0]['metric'] = metric_id

    endpoint = '/api/config/v1/dashboards'
    formatted_slo = json.dumps(synthetic_slo_dashboard, indent=4, sort_keys=False)
    r = put(env, token, endpoint, dashboard_id, formatted_slo)

    if r and 200 < r.status_code < 300:
        print(f'PUT {dashboard_name} to {env}/#dashboard;id={dashboard_id};gf={management_zone_id}')
    print('')


def put_service_slo_dashboard(env_name, env, token, management_zone_name, lookups):

    dashboard_id = get_dashboard_id(management_zone_name, 'SERVICE')

    dashboard_name = f'{management_zone_name} Service SLOs'

    management_zone_id = get_management_zone_id(lookups, env_name, management_zone_name)
    if not management_zone_id:
        print(f'Cannot build Service SLO Dashboard: Management zone not found for "{management_zone_name}"')
        return

    # Service Errors
    management_zone_name_clean = directories_and_files.get_clean_file_name(management_zone_name, '_').replace(' ', '')
    service_errors_metric_id = f'func:slo.{management_zone_name_clean.lower().replace("-", "_")}_service_errors'

    service_errors_metrics_string = f'METRICS=true;LEGEND=true;PROBLEMS=true;decimals=10;customTitle={management_zone_name} - Service Errors;'
    service_errors_slo_name = f'{management_zone_name} - Service Errors'
    service_errors_slo_id = get_slo_id(lookups, env_name, service_errors_slo_name)
    if not service_errors_slo_id:
        print(f'Cannot build Service SLO Dashboard: SLO id not found for "{service_errors_slo_name}"')
        return

    # TODO: This is a hack to get the entity id from an update token to add as dashboard tile reference
    endpoint = '/api/v2/settings/objects'
    url = env + endpoint + '/' + service_errors_slo_id
    settings_object = dynatrace_api.get_without_pagination(url, token).json()

    update_token = settings_object.get('updateToken')
    service_errors_assigned_entity = object_id_to_entity_id(update_token)

    # Service Performance
    management_zone_name_clean = directories_and_files.get_clean_file_name(management_zone_name, '_').replace(' ', '')
    service_performance_metric_id = f'func:slo.{management_zone_name_clean.lower().replace("-", "_")}_service_performance'

    service_performance_metrics_string = f'METRICS=true;LEGEND=true;PROBLEMS=true;decimals=10;customTitle={management_zone_name} - Service Performance;'
    service_performance_slo_name = f'{management_zone_name} - Service Performance'
    service_performance_slo_id = get_slo_id(lookups, env_name, service_performance_slo_name)
    if not service_errors_slo_id:
        print(f'Cannot build Service SLO Dashboard: SLO id not found for "{service_performance_slo_name}"')
        return

    # TODO: This is a hack to get the entity id from an update token to add as dashboard tile reference
    endpoint = '/api/v2/settings/objects'
    url = env + endpoint + '/' + service_performance_slo_id
    # settings_object = get_by_object_id(env, token, endpoint, service_performance_slo_id)
    settings_object = dynatrace_api.get_without_pagination(url, token).json()

    update_token = settings_object.get('updateToken')
    service_performance_assigned_entity = object_id_to_entity_id(update_token)

    service_slo_dashboard = load_service_slo_dashboard_template()

    service_slo_dashboard['id'] = dashboard_id
    service_slo_dashboard['dashboardMetadata']['name'] = dashboard_name
    service_slo_dashboard['dashboardMetadata']['owner'] = 'Admin'
    service_slo_dashboard['dashboardMetadata']['shared'] = True
    service_slo_dashboard['dashboardMetadata']['preset'] = True
    service_slo_dashboard['dashboardMetadata']['dashboardFilter']['managementZone']['id'] = management_zone_id
    service_slo_dashboard['dashboardMetadata']['dashboardFilter']['managementZone']['name'] = management_zone_name
    if service_slo_dashboard.get('dashboardMetadata').get('popularity', None):
        service_slo_dashboard['dashboardMetadata'].pop('popularity')

    tiles = service_slo_dashboard['tiles']

    index = 0
    for tile in tiles:
        if index < 6:
            if tile['tileType'] == 'SLO':
                tile['assignedEntities'] = [service_errors_assigned_entity]
                tile['metric'] = service_errors_metrics_string
                index += 1
            else:
                if tile['tileType'] == 'DATA_EXPLORER' and tile['name'] == '':
                    tile['queries'][0]['metric'] = service_errors_metric_id
                    index += 1
        else:
            if tile['tileType'] == 'SLO':
                tile['assignedEntities'] = [service_performance_assigned_entity]
                tile['metric'] = service_performance_metrics_string
                index += 1
            else:
                if tile['tileType'] == 'DATA_EXPLORER' and tile['name'] == '':
                    tile['queries'][0]['metric'] = service_performance_metric_id
                    index += 1

    endpoint = '/api/config/v1/dashboards'
    formatted_slo = json.dumps(service_slo_dashboard, indent=4, sort_keys=False)
    r = put(env, token, endpoint, dashboard_id, formatted_slo)

    if r and 200 < r.status_code < 300:
        print(f'PUT {dashboard_name} to {env}/#dashboard;id={dashboard_id};gf={management_zone_id}')
    print('')


def put_host_slo_dashboard(env_name, env, token, management_zone_name, lookups):

    dashboard_id = get_dashboard_id(management_zone_name, 'HOST')

    management_zone_id = get_management_zone_id(lookups, env_name, management_zone_name)
    if not management_zone_id:
        print(f'Cannot build Host SLO Dashboard: Management zone not found for "{management_zone_name}"')
        return

    management_zone_name_clean = directories_and_files.get_clean_file_name(management_zone_name, '_').replace(' ', '')

    dashboard_name = f'{management_zone_name} Host SLOs'
    metric_id = f'func:slo.{management_zone_name_clean.lower().replace("-", "_")}_host_availability'
    metrics_string = f'METRICS=true;LEGEND=true;PROBLEMS=true;COLORIZE_BACKGROUND=false;decimals=10;customTitle={management_zone_name} - Host Availability;'
    slo_name = f'{management_zone_name} - Host Availability'

    slo_id = get_slo_id(lookups, env_name, slo_name)
    if not slo_id:
        print(f'Cannot build Host SLO Dashboard: SLO id not found for "{slo_name}"')
        return

    # TODO: This is a hack to get the entity id from an update token to add as dashboard tile reference
    endpoint = '/api/v2/settings/objects'
    url = env + endpoint + '/' + slo_id
    # settings_object = get_by_object_id(env, token, endpoint, slo_id)
    settings_object = dynatrace_api.get_without_pagination(url, token).json()
    update_token = settings_object.get('updateToken')

    assigned_entity = object_id_to_entity_id(update_token)

    host_availability_slo_dashboard = load_host_availability_slo_dashboard_template()

    host_availability_slo_dashboard['id'] = dashboard_id
    host_availability_slo_dashboard['dashboardMetadata']['name'] = dashboard_name
    host_availability_slo_dashboard['dashboardMetadata']['owner'] = 'Admin'
    host_availability_slo_dashboard['dashboardMetadata']['dashboardFilter']['managementZone']['id'] = management_zone_id
    host_availability_slo_dashboard['dashboardMetadata']['dashboardFilter']['managementZone']['name'] = management_zone_name
    if host_availability_slo_dashboard.get('dashboardMetadata').get('popularity', None):
        host_availability_slo_dashboard['dashboardMetadata'].pop('popularity')

    tiles = host_availability_slo_dashboard['tiles']

    for tile in tiles:
        if tile['tileType'] == 'SLO':
            tile['assignedEntities'] = [assigned_entity]
            tile['metric'] = metrics_string
        else:
            if tile['tileType'] == 'DATA_EXPLORER' and tile['name'] == '':
                tile['queries'][0]['metric'] = metric_id

    endpoint = '/api/config/v1/dashboards'
    formatted_slo = json.dumps(host_availability_slo_dashboard, indent=4, sort_keys=False)
    r = put(env, token, endpoint, dashboard_id, formatted_slo)

    if r and 200 < r.status_code < 300:
        print(f'PUT {dashboard_name} to {env}/#dashboard;id={dashboard_id};gf={management_zone_id}')
    print('')


def put(env, token, endpoint, object_id, payload):
    if not allow_rewrites:
        # Testing logic can be uncommented when needed:
        # allow rewrite of host SLO dashboards to fix "preset" issue on initial create
        # allow rewrite of specific SLO dashboards to test
        # if not object_id.startswith('00000001-0000-0000-0003') and not object_id.endswith('000609120517') and not object_id.endswith('000314150304'):
        # if not object_id == '00000001-0000-0000-0000-000136163726':
        if True:
            url = env + endpoint + '/' + object_id
            # if get_by_object_id(env, token, endpoint, object_id):
            if dynatrace_api.get_without_pagination(url, token).json():
                print(f'Skipping dashboard  {object_id} since it already exists!')
                return

    # In general, favor put over post so "fixed ids" can be used
    json_data = json.dumps(json.loads(payload), indent=4, sort_keys=False)
    url = env + endpoint + '/' + object_id
    r = dynatrace_api.put_object(url, token, json_data)
    return r


def get_dashboard_id(management_zone_name, dashboard_type):
    dashboard_type_list = ['HTTP_CHECK', 'SYNTHETIC_TEST', 'SERVICE', 'HOST']

    if dashboard_type not in dashboard_type_list:
        print(f'Unknown dashboard type: {dashboard_type}')
        exit(1)

    suffix = str(dashboard_type_list.index(dashboard_type))

    dashboard_id = convert_string_to_uuid(management_zone_name + suffix)

    return dashboard_id


def convert_string_to_uuid(string):
    numbers = convert_string_to_numbers(string)
    uuid = convert_numbers_to_uuid(numbers)
    return uuid


def convert_string_to_numbers(string):
    string = string.replace(' ', '')
    string = string.replace('App:', '')
    string = string.replace('-', '')
    string = string.replace(':', '')
    numbers = ''
    for character in string.lower():
        if character.isalpha():
            decrement = 96
        else:
            decrement = 18  # Normally it would be 48, but to avoid collisions numbers will be 30 - 39 instead of 00 - 09

        ordinal = ord(character) - decrement
        ordinal_string = f'{ordinal:02}'
        # print(character, ordinal_string)
        numbers += ordinal_string

    return str(numbers)


def convert_numbers_to_uuid(number_string):
    if len(number_string) > 32:
        print('UUID cannot be generated: String converted to numbers is greater than 32 in length')

    number_string_32 = number_string.zfill(32)

    uuid = f'{number_string_32[0:8]}-{number_string_32[8:12]}-{number_string_32[12:16]}-{number_string_32[16:20]}-{number_string_32[20:32]}'

    return str(uuid)


def process(target_env_name, management_zone_name, create_http_check_slo_dashboard, create_browser_slo_dashboard, create_service_slo_dashboard, create_host_slo_dashboard):
    friendly_function_name = 'Dynatrace Automation Tools'

    env_name, env, token = environment.get_environment_for_function_print_control(target_env_name, friendly_function_name, False)

    lookups = load_lookups(target_env_name, env, token)

    if create_http_check_slo_dashboard:
        dashboard_type = 'HTTP_CHECK'
        print(f'Putting {dashboard_type} SLO Dashboard for Management Zone "{management_zone_name}"')
        put_synthetic_slo_dashboard(env_name, env, token, management_zone_name, dashboard_type, lookups)
    if create_browser_slo_dashboard:
        dashboard_type = 'SYNTHETIC_TEST'
        print(f'Putting {dashboard_type} SLO Dashboard for Management Zone "{management_zone_name}"')
        put_synthetic_slo_dashboard(env_name, env, token, management_zone_name, dashboard_type, lookups)
    if create_service_slo_dashboard:
        dashboard_type = 'SERVICE'
        print(f'Putting {dashboard_type} SLO Dashboard for Management Zone "{management_zone_name}"')
        put_service_slo_dashboard(env_name, env, token, management_zone_name, lookups)
    if create_host_slo_dashboard:
        dashboard_type = 'HOST'
        print(f'Putting {dashboard_type} SLO Dashboard for Management Zone "{management_zone_name}"')
        put_host_slo_dashboard(env_name, env, token, management_zone_name, lookups)


def main():
    target_env_name = 'Personal'
    # target_env_name = 'Upper'

    management_zone_name = 'App: KEEP - PROD'

    create_http_check_slo_dashboard = True
    create_browser_slo_dashboard = False
    create_service_slo_dashboard = True
    create_host_slo_dashboard = True

    process(target_env_name, management_zone_name, create_http_check_slo_dashboard, create_browser_slo_dashboard, create_service_slo_dashboard, create_host_slo_dashboard)


if __name__ == '__main__':
    main()
