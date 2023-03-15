import requests
import urllib.parse
import xlsxwriter

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token, mz_name, tag, write_csv, xlsx_data):
    # process_pg(env, token, 'PROCESS_GROUP-689386BDA7C736FD')

    endpoint = '/api/v2/entities'
    entity_selector_param = 'entitySelector=type("PROCESS_GROUP")'
    mz_name_param = f',mzName("{mz_name}")'
    tag_param = f',tag("{tag}")'

    raw_params = entity_selector_param
    if mz_name:
        raw_params += mz_name_param
    if tag:
        raw_params += tag_param

    params = urllib.parse.quote(raw_params, safe='/,=')
    process_group_json_list = dynatrace_api.get(env, token, endpoint, params)

    for process_group_json in process_group_json_list:
        inner_process_group_json_list = process_group_json.get('entities')
        for inner_process_group_json in inner_process_group_json_list:
            entity_id = inner_process_group_json.get('entityId')
            display_name = inner_process_group_json.get('displayName')
            process_pg(env, token, entity_id, display_name, write_csv, mz_name, tag, xlsx_data)


def process_pg(env, token, process_group, display_name, write_csv, mz_name, tag, xlsx_data):
    endpoint = '/api/v1/entity/infrastructure/process-groups/' + process_group + '/logs'
    params = ''
    process_group_logs_json_list = dynatrace_api.get(env, token, endpoint, params)

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

    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, mz_name, tag, write_csv, xlsx_data)


if __name__ == '__main__':
    main()
