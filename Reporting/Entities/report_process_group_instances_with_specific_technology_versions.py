import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


target_management_zones = [
    # 'HostGroup:Laptops',
    'ALINK-PROD',
    'AUTOD-PROD',
]

# Easy hits for testing...
target_technology_types = [
    'DOTNET',
    'DYNATRACE',
    'WINDOWS_SYSTEM',
]


def process(env, token):
    rows = []

    if target_management_zones:
        for target_management_zone in target_management_zones:
            process_entities(env, token, target_management_zone, rows)
    else:
        process_entities(env, token, None, rows)

    rows = remove_duplicates(sorted(rows))
    report_name = 'Technologies'
    report_writer.initialize_text_file(None)
    report_headers = ('Display Name', 'Technology Type', 'Edition', 'Version')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def process_entities(env, token, target_management_zone, rows):
    endpoint = '/api/v2/entities'
    entity_selector = 'type(PROCESS_GROUP_INSTANCE)'
    if target_management_zone:
        entity_selector += f',mzName("{target_management_zone}")'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector) + '&fields=' + urllib.parse.quote('properties.SOFTWARETECHNOLOGIES')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            # entity_id = inner_entities_json.get('entityId')
            # entity_type = inner_entities_json.get('type')
            display_name = inner_entities_json.get('displayName')
            properties = inner_entities_json.get('properties')
            if properties:
                software_technology_list = properties.get('softwareTechnologies')
                if software_technology_list:
                    for software_technology in software_technology_list:
                        software_technology_type = software_technology.get('type')
                        software_technology_edition = software_technology.get('edition')
                        software_technology_version = software_technology.get('version')
                        # print(software_technology, software_technology_type, software_technology_edition, software_technology_version)
                        if software_technology_type and software_technology_edition and software_technology_version:
                        # if software_technology_type and target_technology_types:
                            # if software_technology_type == 'DOTNET' and software_technology_edition == '.NET Framework' and software_technology_version.startswith('3.5'):
                            if software_technology_type in target_technology_types:
                                rows.append((display_name, str(software_technology_type), str(software_technology_edition), str(software_technology_version)))


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
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)


if __name__ == '__main__':
    main()
