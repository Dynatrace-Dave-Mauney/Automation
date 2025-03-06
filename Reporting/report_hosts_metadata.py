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
            # entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')

            properties = inner_entities_json.get('properties')

            tags = inner_entities_json.get('tags', [])

            tag_application, tag_function, tag_environment, tag_full_application = get_specific_tags(tags)

            host_group_name = properties.get('hostGroupName', 'No Host Group')

            rows.append((display_name, host_group_name, tag_application, tag_function, tag_environment, tag_full_application))

        rows = sorted(rows)
        report_name = 'Hosts'
        report_writer.initialize_text_file(None)
        report_headers = ('Host Name', 'Host Group', 'Application Tag', 'Function Tag', 'Environment Tag', 'Full Application Tag')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)


def get_specific_tags(tags):
    specific_tag_keys = ['Application', 'Function', 'Environment', 'Full_Application']
    tag_dict = {'Application': None, 'Function': None, 'Environment': None, 'Full_Application': None}
    for tag in tags:
        # print(tag)
        tag_key = tag.get('key')
        # print('tag_key:', tag_key)
        if tag_key in specific_tag_keys:
            tag_dict[tag_key] = tag.get('value')
            # print('value:', tag.get('value'))

    return tag_dict.get('Application'), tag_dict.get('Function'), tag_dict.get('Environment'), tag_dict.get('Full_Application')


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
    list_str = list_str.replace(' ', '')
    return list_str


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)
    # print(summarize(env, token))

    
if __name__ == '__main__':
    main()
