from inspect import currentframe
import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


target_management_zones = [
    'HostGroup:Laptops',
]

# target_technologies = [
#     'apache',
#     'iis-microsoft',
#     'mysql',
#     'oracledatabase',
#     'oracleweblogic',
#     'sap',
#     'sql-microsoft',
#     'was-liberty-profile',
#     'web-sphere',
# ]

# Using an OS process for testing to guarantee only one process group is affected
target_technologies = [
    'windows',
]

friendly_function_name = 'Dynatrace Automation'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Prod'
# env_name_supplied = 'NonProd'
# env_name_supplied = 'PreProd'
# env_name_supplied = 'Dev'
# env_name_supplied = 'Personal'
env_name_supplied = 'Demo'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)


def process():
    entity_type = 'PROCESS_GROUP'

    process_group_to_update_list = []

    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector) + '&fields=' + urllib.parse.quote('managementZones,icon')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            management_zone_list = inner_entities_json.get('managementZones')
            for management_zone in management_zone_list:
                if management_zone.get('name') in target_management_zones:
                    primary_icon_type = inner_entities_json.get('icon').get('primaryIconType', '')
                    # print(primary_icon_type)
                    if primary_icon_type in target_technologies:
                        print(entity_id + '|' + display_name + '|' + primary_icon_type)
                        process_group_to_update_list.append(entity_id)

    turn_on_process_group_monitoring(process_group_to_update_list)


def turn_on_process_group_monitoring(process_group_to_update_list):
    print('turn_on_process_group_monitoring(' + str(process_group_to_update_list) + ')')
    for process_group_to_update in process_group_to_update_list:
        turn_on_process_group_monitoring_setting(process_group_to_update)


def turn_on_process_group_monitoring_setting(process_group_to_update):
    print('get_process_group_monitoring_setting(' + process_group_to_update + ')')

    put_object_id_list = []
    post_payload_list = []

    endpoint = '/api/v2/settings/objects'
    params = 'schemaIds=' + urllib.parse.quote('builtin:availability.process-group-alerting') + '&scopes=' + process_group_to_update + '&fields=' + urllib.parse.quote('objectId,value')
    settings_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    # print(settings_json_list)
    for settings_json in settings_json_list:
        total_count = settings_json.get('totalCount', '0')
        # print('total_count:', total_count)
        # print('total_count int:', int(total_count))
        if int(total_count) > 0:
            # print('total_count > 0')
            item_list = settings_json.get('items')
            for item in item_list:
                # print(item)
                object_id = item.get('objectId')
                value = item.get('value')
                enabled = value.get('enabled', False)
                if not enabled:
                    print('PUT ' + object_id)
                    put_object_id_list.append(object_id)
        else:
            # print('total_count not > 0')
            print('POST new object')
            payload_string = '{"schemaId": "builtin:availability.process-group-alerting", "scope": "' + process_group_to_update + '", "value": {"enabled": true, "alertingMode": "ON_PGI_UNAVAILABILITY"}}'
            # print(payload_string)
            post_payload_list.append(json.loads(payload_string))

    # print(put_object_id_list)
    # print(post_payload_list)

    if put_object_id_list:
        for put_object_id in put_object_id_list:
            dynatrace_api.put_object(f'{env}{endpoint}/{put_object_id}', token, json.dumps(post_payload_list))

    if post_payload_list:
        dynatrace_api.post_object(f'{env}{endpoint}', token, json.dumps(post_payload_list))


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


if __name__ == '__main__':
    # For testing POST vs PUT you may want to delete an object ID
    # endpoint = '/api/v2/settings/objects'
    # dynatrace_api.delete_object(f'{env}{endpoint}, token, 'vu9U3hXa3q0AAAABACtidWlsdGluOmF2YWlsYWJpbGl0eS5wcm9jZXNzLWdyb3VwLWFsZXJ0aW5nAA1QUk9DRVNTX0dST1VQABAzRjQyODNBMDMwQ0I4Qjg0ACRhZjJlYWRiOS03YjY5LTNlODQtOTllOS03MDQxMzBiZDUwYTO-71TeFdrerQ')
    process()
