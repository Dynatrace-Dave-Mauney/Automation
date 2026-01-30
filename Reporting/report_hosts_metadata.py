import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            display_name = inner_entities_json.get('displayName', '')
            properties = inner_entities_json.get('properties')

            # for property in properties:
            #     print(property, properties.get(property))
            # exit(9999)

            tags = inner_entities_json.get('tags', [])
            tag_application, tag_function, tag_environment, tag_tier, tag_zone, tag_verified = get_specific_tags(tags)
            host_group_name = properties.get('hostGroupName', 'None')
            network_zone = properties.get('networkZone', 'None')
            cloud_type = properties.get('cloudType', 'onprem')
            result, violations_list = audit(display_name, host_group_name, network_zone, cloud_type, tag_application, tag_function, tag_environment, tag_tier, tag_zone, tag_verified)
            result_string = stringify_boolean(result)
            rows.append((display_name, host_group_name, network_zone, cloud_type, tag_application, tag_function, tag_environment, tag_tier, tag_zone, tag_verified, result_string, sort_and_stringify_list_items(violations_list)))

        # for row in rows:
        #     print(row)

        rows = sorted(rows)
        report_name = 'Hosts'
        report_writer.initialize_text_file(None)
        report_headers = ('Host Name', 'Host Group', 'Network Zone', 'Cloud Type', 'Application Tag', 'Function Tag', 'Environment Tag', 'Tier Tag', 'Network Zone Tag', 'Verification Date', 'Audit Status', 'Audit Violations')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)


def audit(display_name, host_group_name, network_zone, cloud_type, tag_application, tag_function, tag_environment, tag_tier, tag_zone, tag_verified):
    function_allow_list = ['app', 'db', 'oracle', 'sql-server', 'web']
    environment_allow_list = ['dev', 'dr', 'other', 'prep', 'prod', 'qa', 'stage', 'test']
    zone_allow_list = ['azure', 'onprem']
    tier_allow_list = ['0', '1']

    result = True
    violations_list = []

    if host_group_name == 'None':
        violations_list.append('Host Group Not Set')
        result = False

    tokens = host_group_name.split('_')
    if len(tokens) != 3:
        violations_list.append('Invalid Host Group Format')
        result = False
    else:
        if tag_application != tokens[0]:
            violations_list.append('Host Group App != App Tag')
            result = False

        if tag_function != tokens[1]:
            violations_list.append('Host Group Function != Function Tag')
            result = False

        if tag_environment != tokens[2]:
            violations_list.append('Host Group Environment != Environment Tag')
            result = False

    if network_zone == 'None':
        violations_list.append('Network Zone Not Set')
        result = False

    if network_zone != tag_zone:
        violations_list.append('Network Zone != Network Zone Tag')
        result = False

    if network_zone not in zone_allow_list:
        violations_list.append('Invalid Network Zone')
        result = False

    if cloud_type.lower() != tag_zone:
        violations_list.append('Network Zone and Cloud Type Mismatch')
        result = False

    # if tag_application == 'None' or tag_function == 'None' or tag_environment == 'None' or tag_tier == 'None' or tag_zone == 'None':
    #     violations_list.append('One or More Tags Not Set')
    #     result = False

    if tag_environment not in environment_allow_list:
        violations_list.append('Invalid Environment Tag')
        result = False

    if tag_zone not in zone_allow_list:
        violations_list.append('Invalid Zone Tag')
        result = False

    if tag_function not in function_allow_list:
        violations_list.append('Invalid Function Tag')
        result = False

    if tag_tier not in tier_allow_list:
        violations_list.append('Invalid Tier Tag')
        result = False

    if tag_zone not in zone_allow_list:
        violations_list.append('Invalid Network Zone Tag')
        result = False

    if result:
        violations_list.append('Audit Passed')

    return result, violations_list


def get_specific_tags(tags):
    specific_tag_keys = ['primary_tags.app', 'primary_tags.function', 'primary_tags.env', 'primary_tags.tier', 'primary_tags.zone', 'verified']
    tag_dict = {}
    for tag in tags:
        tag_key = tag.get('key')
        if tag_key in specific_tag_keys:
            tag_dict[tag_key] = tag.get('value')

    return tag_dict.get('primary_tags.app', 'None'), tag_dict.get('primary_tags.function', 'None'), tag_dict.get('primary_tags.env', 'None'), tag_dict.get('primary_tags.tier', 'None'), tag_dict.get('primary_tags.zone', 'None'), tag_dict.get('verified', 'None')


def sort_and_stringify_dictionary_items(any_dict):
    dict_str = str(sorted(any_dict.items()))
    dict_str = dict_str.replace('[', '')
    dict_str = dict_str.replace(']', '')
    dict_str = dict_str.replace('), (', '~COMMA~')
    dict_str = dict_str.replace('(', '')
    dict_str = dict_str.replace(')', '')
    dict_str = dict_str.replace(',', ':')
    dict_str = dict_str.replace('~COMMA~', ', ')
    dict_str = dict_str.replace("'", "")
    return dict_str


def sort_and_stringify_list_items(any_list):
    list_str = str(sorted(any_list))
    list_str = list_str.replace('[', '')
    list_str = list_str.replace(']', '')
    list_str = list_str.replace("'", "")
    # list_str = list_str.replace(' ', '')
    return list_str


def stringify_boolean(boolean_value):
    if boolean_value:
        return 'Passed'
    else:
        return 'Failed'


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)

    
if __name__ == '__main__':
    main()
