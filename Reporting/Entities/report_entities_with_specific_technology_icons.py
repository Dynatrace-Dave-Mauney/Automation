import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


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
    'dotnet',
]


def process(env, token):
    rows = []

    if target_management_zones:
        for target_management_zone in target_management_zones:
            process_entities(env, token, target_management_zone, rows)
    else:
        process_entities(env, token, None, rows)

    rows = sorted(rows)
    report_name = 'Technologies'
    report_writer.initialize_text_file(None)
    report_headers = ('displayName', 'entityId', 'primaryIconType')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def process_entities(env, token, target_management_zone, rows):
    endpoint = '/api/v2/entities'
    entity_selector = 'type(PROCESS_GROUP)'
    if target_management_zone:
        entity_selector += f',mzName("{target_management_zone}")'
    params = '&pageSize=4000&entitySelector=' + urllib.parse.quote(entity_selector) + '&fields=' + urllib.parse.quote('managementZones,icon')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            # entity_type = inner_entities_json.get('type')
            display_name = inner_entities_json.get('displayName')
            management_zone_list = inner_entities_json.get('managementZones')
            for management_zone in management_zone_list:
                if management_zone.get('name') in target_management_zones:
                    primary_icon_type = inner_entities_json.get('icon').get('primaryIconType', '')
                    if primary_icon_type in target_technologies:
                        rows.append((display_name, entity_id, primary_icon_type))


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)


if __name__ == '__main__':
    main()
