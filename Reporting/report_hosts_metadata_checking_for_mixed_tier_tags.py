import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    app_hosts_by_tier = {}
    rows = []
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST)&from=-5m&fields=properties,tags,managementZones'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            display_name = inner_entities_json.get('displayName', '')
            properties = inner_entities_json.get('properties')

            tags = inner_entities_json.get('tags', [])

            for tag in tags:
                key = tag.get('key')
                if key == 'primary_tags.app':
                    app_value = tag.get('value')
                    # print(app_value)
                if key == 'primary_tags.tier':
                    tier_value = tag.get('value')
                    # print(tier_value)

            hosts_by_tier = app_hosts_by_tier.get(app_value, {})
            hosts_by_tier[tier_value] = hosts_by_tier.get(tier_value, [])
            hosts_by_tier[tier_value].append(display_name)

            app_hosts_by_tier[app_value] = hosts_by_tier

    for app in app_hosts_by_tier.keys():
        tiers = app_hosts_by_tier[app].keys()
        if len(tiers) > 1:
            # print(app, app_hosts_by_tier[app])
            for tier in sorted(tiers):
                for host in app_hosts_by_tier[app][tier]:
                    rows.append((app, tier, host))

    rows = sorted(rows)
    report_name = 'Apps with mixed tier tags'
    report_writer.initialize_text_file(None)
    report_headers = ('Application', 'Tier', 'Host')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def check_for_duplicate_tag_keys(tags):
    all = {}
    dups = []
    for tag in tags:
        key = tag.get('key')
        if 'primary_tags' in key:
            value = tag.get('value')
            # print('key:', key, 'value:', value)
            values = all.get(key, [])
            values.append(value)
            all[key] = values

    for key in all.keys():
        if len(all[key]) > 1:
            dups.append((key, all[key]))

    # if dups:
    #     print(dups)

    return dups


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
