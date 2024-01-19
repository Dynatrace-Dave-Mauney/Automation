import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


host_group_lookup = {}
host_group_auto_update_setting_cache = {}


def load_host_group_lookup():
    global host_group_lookup
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST_GROUP)&to=-24h'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            host_name = inner_entities_json.get('displayName')
            host_id = inner_entities_json.get('entityId')
            host_group_lookup[host_name] = host_id


def get_host_auto_update_setting(host_id):
    endpoint = '/api/config/v1/hosts/' + host_id + '/autoupdate'
    settings_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    settings_json = settings_json_list[0]
    return settings_json.get('setting', 'None')


def get_host_group_auto_update_setting(host_group_id):
    global host_group_auto_update_setting_cache

    if host_group_id == 'None':
        return 'None'

    if host_group_id in host_group_auto_update_setting_cache:
        return host_group_auto_update_setting_cache.get(host_group_id)

    endpoint = '/api/config/v1/hostgroups/' + host_group_id + '/autoupdate'
    settings_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    settings_json = settings_json_list[0]
    return settings_json.get('setting', 'None')


def process():
    rows = []
    global host_group_lookup
    load_host_group_lookup()
    endpoint = '/api/v2/entities'
    # raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-24h&fields=properties,tags'
    raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-24h&fields=properties.installerVersion,tags'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    print('Host Group Name' + '|' + 'Host Name' + '|' + 'Installer Version' + '|' + 'Host Group ID' + '|' + 'Host ID')
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            host_id = inner_entities_json.get('entityId')
            host_name = inner_entities_json.get('displayName')
            properties = inner_entities_json.get('properties')
            installer_version = properties.get('installerVersion')
            tags = inner_entities_json.get('tags', [])

            host_group = 'None'
            for tag in tags:
                if "Host Group" in str(tag):
                    host_group = tag.get('value', 'None')
                if "HostGroup" in str(tag):
                    host_group = tag.get('value', 'None')
                if "Group" in str(tag):
                    host_group = tag.get('value', 'None')
            if host_group == 'NoHostGroup':
                host_group = 'None'

            host_group_id = 'None'
            if host_group != 'None':
                host_group_id = host_group_lookup.get(host_group, 'None')

            # Super slow due to "N+1" problem, so skip and assume "INHERITED" if not modified via automation
            # host_auto_update_setting = get_host_auto_update_setting(host_id)
            # host_group_auto_update_setting = get_host_group_auto_update_setting(host_group_id)

            # print(host_name + '|' + host_id + '|' + host_group + '|' + host_group_id)
            # print(host_group + '|' + host_name + '|' + host_group_id + '|' + host_id)

            rows.append((host_group, host_name, installer_version, host_group_id, host_id))

    sorted_rows = sorted(rows, key=lambda row: row[0].lower())

    report_name = 'Host Group Auto Update Details'
    report_headers = ('Host Group Name', 'Host Name', 'Installer Version', 'Host Group ID', 'Host ID', 'Scope', 'Setting')

    report_writer.write_console(report_name, report_headers, sorted_rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, sorted_rows, header_format=None, auto_filter=(0, len(report_headers)))


if __name__ == '__main__':
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

    process()
