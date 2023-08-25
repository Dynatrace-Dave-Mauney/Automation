import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


target_management_zones = [
    'HostGroup:Laptops',
]


def process(env, token, entity_type):
    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector) + '&fields=' + urllib.parse.quote('properties.SOFTWARETECHNOLOGIES')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    # print(entities_json_list)
    # exit(1234)

    headers = ('Process Name', 'Technology Type', 'Technology Edition', 'Technology Version')
    # print('displayName')

    rows = []

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            # print(inner_entities_json)
            # entity_id = inner_entities_json.get('entityId')
            # entity_type = inner_entities_json.get('type')
            display_name = inner_entities_json.get('displayName')
            properties = inner_entities_json.get('properties')
            # print(properties)
            # exit(1234)
            if properties:
                software_technology_list = properties.get('softwareTechnologies')
                # print(software_technology_list)
                if software_technology_list:
                    for software_technology in software_technology_list:
                        software_technology_type = software_technology.get('type')
                        software_technology_edition = software_technology.get('edition')
                        software_technology_version = software_technology.get('version')
                        if software_technology_type and software_technology_edition and software_technology_version:
                            # print(entity_id + '|' + display_name + '|' + software_technology_type + '|' + software_technology_edition + '|' + software_technology_version)
                            rows.append((display_name, software_technology_type, software_technology_edition, software_technology_version))

    sorted_rows = remove_duplicates(sorted(rows, key=lambda row: str(row[0]).lower()))

    report_writer.write_console('Process Technologies', headers, sorted_rows, '|')
    report_writer.write_xlsx('process_tech.xlsx', 'Process Technologies', headers, sorted_rows, None, None)


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    # friendly_function_name = 'RobotAdmin'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token, 'PROCESS_GROUP_INSTANCE')


if __name__ == '__main__':
    main()
