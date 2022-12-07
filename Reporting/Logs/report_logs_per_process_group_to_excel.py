import os
import requests
import xlsxwriter


def process(env, token, mz_name, tag, write_csv, xlsx_data):
    # process_pg(env, token, 'PROCESS_GROUP-689386BDA7C736FD')

    endpoint = '/api/v2/entities'
    params = 'entitySelector=type%28%22PROCESS_GROUP%22%29'
    if mz_name is not None:
        params = params + '%2CmzName%28%22' + mz_name + '%22%29'
    if tag is not None:
        tag = tag.replace(':', '%3A')
        params = params + '%2Ctag%28%22' + tag + '%22%29'
    process_group_json_list = get_rest_api_json(env, token, endpoint, params)

    for process_group_json in process_group_json_list:
        inner_process_group_json_list = process_group_json.get('entities')
        for inner_process_group_json in inner_process_group_json_list:
            entity_id = inner_process_group_json.get('entityId')
            display_name = inner_process_group_json.get('displayName')
            process_pg(env, token, entity_id, display_name, write_csv, mz_name, tag, xlsx_data)


def process_pg(env, token, process_group, display_name, write_csv, mz_name, tag, xlsx_data):
    endpoint = '/api/v1/entity/infrastructure/process-groups/' + process_group + '/logs'
    params = ''
    process_group_logs_json_list = get_rest_api_json(env, token, endpoint, params)

    for process_group_logs_json in process_group_logs_json_list:
        inner_process_group_logs_json_list = process_group_logs_json.get('logs')
        for inner_process_group_logs_json in inner_process_group_logs_json_list:
            path = inner_process_group_logs_json.get('path')
            output = display_name + ':' + path
            print(output)
            if write_csv:
                data = [display_name, path]
                xlsx_data.append(data)

    if write_csv:
        write_xlsx(xlsx_data, mz_name, tag)


def write_xlsx(xlsx_data, mz_name, tag):
    filename_prefix = 'LogsPerProcessGroup'
    if mz_name is not None:
        filename_prefix += '_MZ-' + mz_name
    if tag is not None:
        filename_prefix += '_TAG-' + tag
    workbook = xlsxwriter.Workbook('../../$Output/Reporting/' + filename_prefix + '.xlsx')
    worksheet = workbook.add_worksheet('Logs Summary')

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True})

    # Write headers in bold
    worksheet.write('A1', 'Process Group Name', bold)
    worksheet.write('B1', 'Log File Path', bold)

    row = 1

    for inner_list in xlsx_data:
        # print(str(row) + ':' + str(inner_list))
        for display_name, log_path in [inner_list]:
            worksheet.write(row, 0, display_name)
            worksheet.write(row, 1, log_path)
        row += 1

    workbook.close()


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    json_data = resp.json()

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json_data) is list:
        # DEBUG:
        # print(json_data)
        return json_data

    json_list = [json_data]
    next_page_key = json_data.get('nextPageKey')

    while next_page_key is not None:
        # next_page_key = next_page_key.replace('=', '%3D') # Ths does NOT help.  Also, equals are apparently fine in params.
        # print(f'next_page_key: {next_page_key}')
        params = {'nextPageKey': next_page_key}
        full_url = url + endpoint
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
        # print(resp.url)

        if resp.status_code != 200:
            print('Paginated REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            exit(1)

        json_data = resp.json()
        # print(json_data)

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def main():
    xlsx_data = []
    # mz_name = 'HostGroup:Laptops'
    # mz_name = 'Selective'
    # mz_name = 'OCF_PIC'
    # tag = 'Tech:Jetty'
    # tag = 'Tech:Java'
    # tag = 'Tech:.NET'
    mz_name = None
    tag = None
    write_csv = True

    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, mz_name, tag, write_csv, xlsx_data)


if __name__ == '__main__':
    main()
