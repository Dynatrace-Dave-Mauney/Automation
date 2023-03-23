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
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            host_name = inner_entities_json.get('displayName')
            host_id = inner_entities_json.get('entityId')
            host_group_lookup[host_name] = host_id


def get_host_auto_update_setting(host_id):
    endpoint = '/api/config/v1/hosts/' + host_id + '/autoupdate'
    settings_json_list = dynatrace_api.get(env, token, endpoint, '')
    settings_json = settings_json_list[0]
    return settings_json.get('setting', 'None')


def get_host_group_auto_update_setting(host_group_id):
    global host_group_auto_update_setting_cache

    if host_group_id == 'None':
        return 'None'

    if host_group_id in host_group_auto_update_setting_cache:
        return host_group_auto_update_setting_cache.get(host_group_id)

    endpoint = '/api/config/v1/hostgroups/' + host_group_id + '/autoupdate'
    settings_json_list = dynatrace_api.get(env, token, endpoint, '')
    settings_json = settings_json_list[0]
    return settings_json.get('setting', 'None')


def process():
    xlsx_file_name = 'autoupdate.xlsx'
    rows = []
    global host_group_lookup
    load_host_group_lookup()
    endpoint = '/api/v2/entities'
    # raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-24h&fields=properties,tags'
    raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-24h&fields=properties.installerVersion,tags'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
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

    write_console(sorted(rows, key=lambda row: row[0].lower()))
    write_xlsx(xlsx_file_name, sorted(rows, key=lambda row: row[0].lower()))


def write_console(rows):
    title = 'Host Group Auto Update Details'
    headers = ('Host Group Name', 'Host Name', 'Installer Version', 'Host Group ID', 'Host ID', 'Scope', 'Setting')
    delimiter = '|'
    report_writer.write_console(title, headers, rows, delimiter)


def write_xlsx(xlsx_file_name, rows):
    worksheet_name = 'Host Group Auto Update Details'
    headers = ('Host Group Name', 'Host Name', 'Installer Version', 'Host Group ID', 'Host ID', 'Scope', 'Setting')
    header_format = None
    auto_filter = (0, len(headers))
    report_writer.write_xlsx(xlsx_file_name, worksheet_name, headers, rows, header_format, auto_filter)


if __name__ == '__main__':
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process()
