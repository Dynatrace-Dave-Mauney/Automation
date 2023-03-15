import requests
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

# Easy hits for testing...
target_technologies = [
    'dynatrace',
    'windows',
]


def process(env, token, entity_type):
    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector) + '&fields=' + urllib.parse.quote('managementZones,icon')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    # print(entities_json_list)

    print('entityId' + '|' + 'displayName')

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            # print(inner_entities_json)
            entity_id = inner_entities_json.get('entityId')
            # entity_type = inner_entities_json.get('type')
            display_name = inner_entities_json.get('displayName')
            management_zone_list = inner_entities_json.get('managementZones')
            for management_zone in management_zone_list:
                if management_zone.get('name') in target_management_zones:
                    primary_icon_type = inner_entities_json.get('icon').get('primaryIconType', '')
                    if primary_icon_type in target_technologies:
                        print(entity_id + '|' + display_name + '|' + primary_icon_type)


def main():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, 'PROCESS_GROUP')


if __name__ == '__main__':
    main()
