import os
import requests
import urllib.parse
import xlsxwriter

host_group_lookup = {}
host_group_auto_update_setting_cache = {}
report = []

def get_rest_api_json(url, token, endpoint, params):
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    json = resp.json()

    if type(json) is list:
        return json

    json_list = [json]
    next_page_key = json.get('nextPageKey')

    while next_page_key is not None:
        params = {'nextPageKey': next_page_key}
        full_url = url + endpoint
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})

        if resp.status_code != 200:
            print('Paginated REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            exit(1)

        json = resp.json()

        next_page_key = json.get('nextPageKey')
        json_list.append(json)

    return json_list


def load_host_group_lookup():
    global host_group_lookup
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST_GROUP)&to=-24h'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = get_rest_api_json(env, token, endpoint, params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            host_name = inner_entities_json.get('displayName')
            host_id = inner_entities_json.get('entityId')
            host_group_lookup[host_name] = host_id


def get_host_auto_update_setting(host_id):
    endpoint = '/api/config/v1/hosts/' + host_id + '/autoupdate'
    settings_json_list = get_rest_api_json(env, token, endpoint, '')
    settings_json = settings_json_list[0]
    return settings_json.get('setting', 'None')


def get_host_group_auto_update_setting(host_group_id):
    global host_group_auto_update_setting_cache

    if host_group_id == 'None':
        return 'None'

    if host_group_id in host_group_auto_update_setting_cache:
        return host_group_auto_update_setting_cache.get(host_group_id)

    endpoint = '/api/config/v1/hostgroups/' + host_group_id + '/autoupdate'
    settings_json_list = get_rest_api_json(env, token, endpoint, '')
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
    entities_json_list = get_rest_api_json(env, token, endpoint, params)
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
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')
    # env_name, tenant_key, token_key = ('FreeTrial1', 'FREETRIAL1_TENANT', 'ROBOT_ADMIN_FREETRIAL1_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

    print(f'Environment Name: {env_name}')
    print(f'Environment:      {env}')
    print(f'Token:            {masked_token}')

    print('')
    print('Host Group Auto Update Details')

    process(env, token)
