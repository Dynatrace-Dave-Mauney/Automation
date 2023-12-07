"""

PUT SLO dashboards based on a template after changing the necessary fields.

"""

import base64
import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


lookups = {}
slo_dashboard_prefix = 'FF000001-0000-0000-0000-'

friendly_function_name = 'Dynatrace Automation Tools'


def process():
    dashboard_put_count = 0

    # Fake examples
    asn_list = [
        'FAKE1-PROD',
        'FAKE2-PROD',
    ]

    for asn in asn_list:
        dash_index = asn.find('-') + 1
        env = asn[dash_index:]
        target_env_name = ''
        if env == 'PROD':
            target_env_name = 'Prod'
        else:
            if env in ['DEV', 'STG']:
                target_env_name = 'NonProd'
            else:
                print('Unsupported target environment!')
        print(f'Procssing ASN "{asn}" with target environment of "{target_env_name}"')

        put_default_http_check_availability_slo_dashboard(target_env_name=target_env_name, monitor_name=asn)
        # put_default_service_slo_dashboard(target_env_name=target_env_name, asn=asn)
        dashboard_put_count += 1

    print(f'{dashboard_put_count} dashboards were put')


def load_lookups(target_env_name):
    global lookups

    if target_env_name not in lookups:
        lookups = {target_env_name: {'management_zones': {}, 'metrics': {}, 'slos': {}}}
        load_lookup_management_zones(target_env_name)
        load_lookup_metrics(target_env_name)
        load_lookup_slos(target_env_name)

    # print('DEBUG lookups:')
    # print(lookups)


def load_lookup_management_zones(target_env_name):
    global lookups

    env_name, env, token = environment.get_environment_for_function_print_control(target_env_name, friendly_function_name, False)

    endpoint = '/api/config/v1/managementZones'
    management_zones_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        for inner_management_zones_json in inner_management_zones_json_list:
            management_zone_id = inner_management_zones_json.get('id')
            management_zone_name = inner_management_zones_json.get('name')
            lookups[target_env_name]['management_zones'][management_zone_name] = management_zone_id


def load_lookup_metrics(target_env_name):
    global lookups

    env_name, env, token = environment.get_environment_for_function_print_control(target_env_name, friendly_function_name, False)

    endpoint = '/api/v2/metrics'
    params = 'text=func:slo'
    metrics_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for metrics_json in metrics_json_list:
        inner_metrics_json_list = metrics_json.get('metrics')
        for inner_metrics_json in inner_metrics_json_list:
            metric_id = inner_metrics_json.get('metricId')
            metric_name = inner_metrics_json.get('displayName')
            if 'burn' not in metric_id and 'Budget' not in metric_id:
                lookups[target_env_name]['metrics'][metric_id] = metric_name


def load_lookup_slos(target_env_name):
    global lookups

    env_name, env, token = environment.get_environment_for_function_print_control(target_env_name, friendly_function_name, False)

    endpoint = '/api/v2/settings/objects'
    raw_params = 'schemaIds=builtin:monitoring.slo'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    slos_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for slos_json in slos_json_list:
        inner_slos_json_list = slos_json.get('items')
        for inner_slos_json in inner_slos_json_list:
            slo_id = inner_slos_json.get('objectId')
            slo_name = inner_slos_json.get('value').get('name')
            if 'Synthetic Availability (HTTP)' in slo_name or '- Service Errors' in slo_name or '- Service Performance' in slo_name:
                lookups[target_env_name]['slos'][slo_name] = slo_id


def get_management_zone_id(target_env_name, management_zone_name):
    try:
        management_zone_id = lookups[target_env_name]['management_zones'][management_zone_name]
        return management_zone_id
    except KeyError:
        print(f'Management Zone ID lookup failed for {management_zone_name} in environment {target_env_name}')
        exit(1)


def get_metric_name(target_env_name, metric_id):
    try:
        metric_name = lookups[target_env_name]['metrics'][metric_id]
        return metric_name
    except KeyError:
        print(f'Metric name lookup failed for {metric_id} in environment {target_env_name}')
        exit(1)


def get_slo_id(target_env_name, slo_name):
    try:
        slo_id = lookups[target_env_name]['slos'][slo_name]
        return slo_id
    except KeyError:
        print(f'SLO ID lookup failed for {slo_name} in environment {target_env_name}')
        exit(1)


def object_id_to_entity_id(object_id):
    # Add double equals to force pad regardless of remainder
    # https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding/49459036#49459036
    decoded_object_id_bytes = base64.urlsafe_b64decode(object_id + '==')

    # Remove the first 13 bytes and remove the bytes indicator while converting to a string
    schema_id = str(decoded_object_id_bytes[12:]).replace("b'", "")

    # Truncate after the first byte delimiter that indicates the end of the schema id
    entity_id = schema_id[:schema_id.find('\\')]

    # print(f'DEBUG object_id_to_entity_id parameters - entity_id: "{entity_id}" for object_id: {object_id} ')

    return entity_id


def put_default_http_check_availability_slo_dashboard(target_env_name, monitor_name):
    load_lookups(target_env_name)

    owner = 'dave.mauney@dynatrace.com'
    put_http_check_availability_slo_dashboard(target_env_name, monitor_name, owner)


def load_http_check_availability_slo_dashboard_template():
    with open('http_check_availability_slo_dashboard_template.json', 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def put_default_service_slo_dashboard(target_env_name, asn):
    load_lookups(target_env_name)
    owner = 'dave.mauney@dynatrace.com'
    put_service_slo_dashboard(target_env_name, asn, owner)


def load_service_slo_dashboard_template():
    with open('service_slo_dashboard_template.json', 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def convert_asn_to_numbers(asn):
    numbers = ''
    for character in asn.lower():
        if character.isalpha():
            decrement = 96
        else:
            decrement = 18  # Normally it would be 48, but to avoid collisions numbers will be 30 - 39 instead of 00 - 09

        ordinal = ord(character) - decrement
        ordinal_string = f'{ordinal:02}'
        # print(character, ordinal_string)
        numbers += ordinal_string

    return str(numbers)


def put_http_check_availability_slo_dashboard(target_env_name, monitor_name, owner):
    env_name, env, token = environment.get_environment_for_function_print_control(target_env_name, friendly_function_name, False)

    dash_index = monitor_name.find('-')

    asn = monitor_name[0:dash_index]
    monitor_env = monitor_name[dash_index+1:]

    # Always keep the order of existing items when adding new ones!!!
    monitor_env_list = ['PROD', 'DEV', 'STG', 'UAT', 'QA', 'TEST']

    if monitor_env not in monitor_env_list:
        print(f'Unknown monitor environment: {monitor_env}')
        print(asn, monitor_name, monitor_env)
        exit(1)

    monitor_env_index = monitor_env_list.index(monitor_env)
    monitor_env_number = f'{monitor_env_index:02}'

    dashboard_id = slo_dashboard_prefix + monitor_env_number + convert_asn_to_numbers(asn)
    dashboard_name = f'{monitor_name} SLOs'

    management_zone_id = get_management_zone_id(target_env_name, monitor_name)
    # print('DEBUG put_http_check_availability_slo_dashboard management zone details:', management_zone_id, monitor_name)

    metric_id = f'func:slo.{monitor_name.lower().replace("-", "_")}_synthetic_availability'
    # metric_name = get_metric_name(target_env_name, metric_id)
    # print('DEBUG put_http_check_availability_slo_dashboard metric details:', metric_id, metric_name')

    metrics_string = f'METRICS=true;LEGEND=true;PROBLEMS=true;decimals=10;customTitle={monitor_name} - Synthetic Availability (HTTP);'

    slo_name = f'{monitor_name} - Synthetic Availability (HTTP)'
    slo_id = get_slo_id(target_env_name, slo_name)
    # print(f'DEBUG put_http_check_availability_slo_dashboard slo details: slo_id: {slo_id} slo_name: {slo_name}')

    # TODO: This is a hack to get the entity id from an update token to add as dashboard tile reference
    endpoint = '/api/v2/settings/objects'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{slo_id}', token)
    settings_object = r.json()
    update_token = settings_object.get('updateToken')
    # print('DEBUG put_http_check_availability_slo_dashboard update token decode details:', slo_id, slo_name, update_token)

    assigned_entity = object_id_to_entity_id(update_token)

    http_check_availability_slo_dashboard = load_http_check_availability_slo_dashboard_template()

    http_check_availability_slo_dashboard['id'] = dashboard_id
    http_check_availability_slo_dashboard['dashboardMetadata']['name'] = dashboard_name
    http_check_availability_slo_dashboard['dashboardMetadata']['owner'] = owner
    http_check_availability_slo_dashboard['dashboardMetadata']['dashboardFilter']['managementZone']['id'] = management_zone_id
    http_check_availability_slo_dashboard['dashboardMetadata']['dashboardFilter']['managementZone']['name'] = monitor_name
    http_check_availability_slo_dashboard['dashboardMetadata'].pop('popularity')

    tiles = http_check_availability_slo_dashboard['tiles']

    for tile in tiles:
        if tile['tileType'] == 'SLO':
            tile['assignedEntities'] = [assigned_entity]
            tile['metric'] = metrics_string
        else:
            if tile['tileType'] == 'DATA_EXPLORER' and tile['name'] == '':
                tile['queries'][0]['metric'] = metric_id

    endpoint = '/api/config/v1/dashboards'
    formatted_slo = json.dumps(http_check_availability_slo_dashboard, indent=4, sort_keys=False)
    dynatrace_api.put_object(f'{env}{endpoint}/{dashboard_id}', token, formatted_slo)
    print(f'PUT {monitor_name} dashboard to {env_name} ({env}) with id: {dashboard_id}')
    print('')


def put_service_slo_dashboard(target_env_name, asn, owner):
    env_name, env, token = environment.get_environment_for_function_print_control(target_env_name, friendly_function_name, False)

    dash_index = asn.find('-')

    asn_proper = asn[0:dash_index]
    asn_env = asn[dash_index+1:]

    # Always keep the order of existing items when adding new ones!!!
    # The index is used in the dashboard id.
    # TODO: Make global (used two places now)
    env_list = ['PROD', 'DEV', 'STG', 'UAT', 'QA', 'TEST']

    if asn_env not in env_list:
        print(f'Unknown asn environment: {asn_env}')
        print(asn, asn_proper, asn_env)
        exit(1)

    env_index = env_list.index(asn_env)
    asn_env_number = f'{env_index:02}'

    dashboard_id = slo_dashboard_prefix + asn_env_number + convert_asn_to_numbers(asn_proper)
    dashboard_name = f'{asn} Service SLOs'

    management_zone_id = get_management_zone_id(target_env_name, asn)

    # Service Errors
    service_errors_metric_id = f'func:slo.{asn.lower().replace("-", "_")}_service_errors'
    service_errors_metrics_string = f'METRICS=true;LEGEND=true;PROBLEMS=true;decimals=10;customTitle={asn} - Service Errors;'
    service_errors_slo_name = f'{asn} - Service Errors'
    service_errors_slo_id = get_slo_id(target_env_name, service_errors_slo_name)
    # TODO: This is a hack to get the entity id from an update token to add as dashboard tile reference
    endpoint = '/api/v2/settings/objects'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{service_errors_slo_id}', token)
    settings_object = r.json()
    update_token = settings_object.get('updateToken')
    service_errors_assigned_entity = object_id_to_entity_id(update_token)

    # Service Performance
    service_performance_metric_id = f'func:slo.{asn.lower().replace("-", "_")}_service_performance'
    service_performance_metrics_string = f'METRICS=true;LEGEND=true;PROBLEMS=true;decimals=10;customTitle={asn} - Service Performance;'
    service_performance_slo_name = f'{asn} - Service Performance'
    service_performance_slo_id = get_slo_id(target_env_name, service_performance_slo_name)
    # TODO: This is a hack to get the entity id from an update token to add as dashboard tile reference
    endpoint = '/api/v2/settings/objects'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{service_performance_slo_id}', token)
    settings_object = r.json()
    update_token = settings_object.get('updateToken')
    service_performance_assigned_entity = object_id_to_entity_id(update_token)

    service_slo_dashboard = load_service_slo_dashboard_template()

    service_slo_dashboard['id'] = dashboard_id
    service_slo_dashboard['dashboardMetadata']['name'] = dashboard_name
    service_slo_dashboard['dashboardMetadata']['owner'] = owner
    service_slo_dashboard['dashboardMetadata']['shared'] = True
    service_slo_dashboard['dashboardMetadata']['preset'] = True
    service_slo_dashboard['dashboardMetadata']['dashboardFilter']['managementZone']['id'] = management_zone_id
    service_slo_dashboard['dashboardMetadata']['dashboardFilter']['managementZone']['name'] = asn_proper

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
    dynatrace_api.put_object(f'{env}{endpoint}/{dashboard_id}', token, formatted_slo)
    print(f'PUT {asn} dashboard to {env_name} ({env}) with id: {dashboard_id}')
    print('')


def main():
    process()


if __name__ == '__main__':
    main()
