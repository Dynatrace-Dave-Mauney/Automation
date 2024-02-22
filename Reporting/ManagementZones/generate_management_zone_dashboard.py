import copy
import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
# from Reuse import report_writer

entity_types_of_interest = [
    # HOST is a proxy for PROCESS...
    # MOBILE_APPLICATION is not needed yet since no MZ is used for the one that exists
    # TODO: KUBERNETES will be added later.  It is just "side menu" stuff
    'APPLICATION',
    'BROWSER',
    'HTTP_CHECK',
    'SERVICE',
    'DATABASE_SERVICE',
    'HOST',
    # 'KUBERNETES_CLUSTER',
    # 'KUBERNETES_NODE',
    # 'KUBERNETES_SERVICE',
]


def process(env, token):
    if 'DATABASE_SERVICE' in entity_types_of_interest and 'SERVICE' not in entity_types_of_interest:
        print('The "entity_types_of_interest" list must include "SERVICE" if "DATABASE_SERVICE" is included.')
        exit(1)

    mz_coverage_dict = {}
    mz_id_lookup_dict = {}

    counts_by_entity_type_template = {}
    for entity_type_of_interest in entity_types_of_interest:
        counts_by_entity_type_template[entity_type_of_interest] = 0

    endpoint = '/api/config/v1/managementZones'
    management_zone_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for management_zone_json in management_zone_json_list:
        inner_management_zone_json_list = management_zone_json.get('values')
        for inner_management_zone_json in inner_management_zone_json_list:
            mz_name = inner_management_zone_json.get('name')
            mz_id = inner_management_zone_json.get('id')
            mz_coverage_dict[mz_name] = copy.deepcopy(counts_by_entity_type_template)
            mz_id_lookup_dict[mz_name] = mz_id

    for entity_type_of_interest in entity_types_of_interest:
        get_mz_coverage_for_entity_type(env, token, entity_type_of_interest, mz_coverage_dict)

    for key in sorted(mz_coverage_dict.keys()):
        mz_id = mz_id_lookup_dict.get(key).zfill(19)
        mz_dashboard_id = convert_mz_id_to_db_id(mz_id)
        print(key, mz_id, mz_dashboard_id, get_entity_type_list(key, mz_coverage_dict))

        dashboard_template = get_dashboard_template(env, token)
        dashboard = copy.deepcopy(dashboard_template)
        dashboard['id'] = mz_dashboard_id
        dashboard_template_name = dashboard.get('dashboardMetadata').get('name')
        dashboard['dashboardMetadata']['name'] = f'{dashboard_template_name} for {key}'
        dashboard['dashboardMetadata']['dashboardFilter'] = {"managementZone": {"id": mz_id, "name": key}}
        print(dashboard)


def convert_mz_id_to_db_id(mz_id):
    # drop the negative sign, if present and start number with 1 instead.
    # start positive numbers with 2 so that positive and negative numbers are both of the same length (20) an remain unique.
    if mz_id.startswith('-'):
        mz_id = '1' + mz_id.replace('-', '')
    else:
        mz_id = '2' + mz_id

    mz_id_string = str(mz_id)
    dashboard_id = f'00000000-dddd-{mz_id_string[0:4]}-{mz_id_string[4:8]}-{mz_id_string[8:20]}'

    return dashboard_id


def get_dashboard_template(env, token):
    dashboard_template_id = '00000000-dddd-bbbb-ffff-000000000001'
    endpoint = '/api/config/v1/dashboards'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{dashboard_template_id}', token)
    dashboard_template = json.loads(r.text)
    return dashboard_template


def get_entity_type_list(management_zone_name, mz_coverage_dict):
    entity_type_list = []
    for entity_type in entity_types_of_interest:
        count = mz_coverage_dict.get(management_zone_name).get(entity_type)
        if count > 0:
            entity_type_list.append(entity_type)

    return entity_type_list


def get_mz_coverage_for_entity_type(env, token, entity_type, mz_coverage_dict):
    # Skip special entity types used for counting only
    # Database services will be counted when the SERVICE entity type is processed
    if entity_type == 'DATABASE_SERVICE':
        return

    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    raw_params = f'&entitySelector={entity_selector}&fields=managementZones'
    if entity_type == 'SERVICE':
        raw_params += ',properties.serviceType'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            management_zone_list = inner_entities_json.get('managementZones')
            if management_zone_list:
                if entity_type == 'SERVICE' and inner_entities_json.get('properties').get('serviceType') == 'DATABASE_SERVICE' and 'DATABASE_SERVICE' in entity_types_of_interest:
                    increment_mz_coverage_dict_counts('DATABASE_SERVICE', management_zone_list, mz_coverage_dict)
                else:
                    increment_mz_coverage_dict_counts(entity_type, management_zone_list, mz_coverage_dict)


def increment_mz_coverage_dict_counts(entity_type, management_zone_list, mz_coverage_dict):
    for management_zone in management_zone_list:
        mz_name = management_zone.get('name')
        mz_coverage_dict[mz_name][entity_type] += 1


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    _, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
