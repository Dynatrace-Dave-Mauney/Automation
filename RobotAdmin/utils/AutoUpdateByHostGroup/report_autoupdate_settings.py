import os
import requests
import urllib.parse
import xlsxwriter

from Reuse import dynatrace_api
from Reuse import environment


host_group_lookup = {}
host_group_auto_update_setting_cache = {}
report = []

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


def process(env, token):
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
            line = host_group + '|' + host_name + '|' + str(installer_version) + '|' + host_group_id + '|' + host_id
            report.append(line)

            columns = []
            columns.append(host_group)
            columns.append(host_name)
            columns.append(str(installer_version))
            columns.append(host_group_id)
            columns.append(host_id)
            rows.append(columns)

    for line in sorted(report):
        print(line)

    # for row in sorted(rows):
    #     print(row)

    write_xlsx_from_list(sorted(rows))


def write_xlsx_from_list(rows):
    workbook = xlsxwriter.Workbook('autoupdate.xlsx')
    worksheet = workbook.add_worksheet()

    row_index = 0
    column_index = 0

    headers = ['Host Group Name', 'Host Name', 'Installer Version', 'Host Group ID', 'Host ID', 'Scope', 'Setting']

    worksheet.write(row_index, 0, headers[0])
    worksheet.write(row_index, 1, headers[1])
    worksheet.write(row_index, 2, headers[2])
    worksheet.write(row_index, 3, headers[3])
    worksheet.write(row_index, 4, headers[4])
    worksheet.write(row_index, 5, headers[5])
    worksheet.write(row_index, 6, headers[6])
    row_index += 1

    for row in rows:
        worksheet.write(row_index, 0, row[0])
        worksheet.write(row_index, 1, row[1])
        worksheet.write(row_index, 2, row[2])
        worksheet.write(row_index, 3, row[3])
        worksheet.write(row_index, 4, row[4])
        row_index += 1

    workbook.close()


if __name__ == '__main__':
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    print('Host Group Auto Update Details')

    process(env, token)
