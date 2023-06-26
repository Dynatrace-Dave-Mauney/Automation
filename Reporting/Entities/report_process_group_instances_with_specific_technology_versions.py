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
    params = '&entitySelector=' + urllib.parse.quote(entity_selector) + '&fields=' + urllib.parse.quote('properties.SOFTWARETECHNOLOGIES')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    # print(entities_json_list)
    # exit(1234)
    print('entityId' + '|' + 'displayName')

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            # print(inner_entities_json)
            entity_id = inner_entities_json.get('entityId')
            # entity_type = inner_entities_json.get('type')
            display_name = inner_entities_json.get('displayName')
            properties = inner_entities_json.get('properties')
            # print(properties)
            # exit(1234)
            if properties:
                software_technology_list = properties.get('softwareTechnologies')
                if software_technology_list:
                    for software_technology in software_technology_list:
                        software_technology_type = software_technology.get('type')
                        software_technology_edition = software_technology.get('edition')
                        software_technology_version = software_technology.get('version')
                        if software_technology_type and software_technology_edition and software_technology_version:
                            if software_technology_type == 'DOTNET' and software_technology_edition == '.NET Framework' and software_technology_version.startswith('3.5'):
                                print(entity_id + '|' + display_name + '|' + software_technology.get('version'))


def main():
    env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('NonProd')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    # env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, 'PROCESS_GROUP_INSTANCE')


if __name__ == '__main__':
    main()
