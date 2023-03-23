# TODO: Test this module after the refactoring to use report_writer.  This is currently not possible due to token permissions...

import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token, mz_name, tag, write_excel):
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
            process_pg(env, token, entity_id, display_name, write_excel, mz_name, tag)


def process_pg(env, token, process_group, display_name, write_excel, mz_name, tag):
    rows = []
    endpoint = '/api/v1/entity/infrastructure/process-groups/' + process_group + '/logs'
    params = ''
    process_group_logs_json_list = dynatrace_api.get(env, token, endpoint, params)

    for process_group_logs_json in process_group_logs_json_list:
        inner_process_group_logs_json_list = process_group_logs_json.get('logs')
        for inner_process_group_logs_json in inner_process_group_logs_json_list:
            path = inner_process_group_logs_json.get('path')
            rows.append((display_name, path))

    write_console(rows)
    if write_excel:
        write_xlsx(rows, mz_name, tag)


def write_console(rows):
    title = 'Logs Per Process Group'
    headers = ('Process Group Name', 'Log File Path')
    delimiter = '|'
    report_writer.write_console(title, headers, rows, delimiter)


def write_xlsx(rows, mz_name, tag):
    filename_prefix = 'LogsPerProcessGroup'
    if mz_name is not None:
        filename_prefix += '_MZ-' + mz_name
    if tag is not None:
        filename_prefix += '_TAG-' + tag
    xlsx_file_name = f'../../$Output/Reporting/{filename_prefix}.xlsx'

    worksheet_name = 'Logs Per Process Group'
    headers = ('Process Group Name', 'Log File Path')
    header_format = None
    auto_filter = (0, len(headers))
    report_writer.write_xlsx(xlsx_file_name, worksheet_name, headers, rows, header_format, auto_filter)


def main():
    # mz_name = 'HostGroup:Laptops'
    # mz_name = 'Selective'
    # mz_name = 'OCF_PIC'
    # tag = 'Tech:Jetty'
    # tag = 'Tech:Java'
    # tag = 'Tech:.NET'
    mz_name = None
    tag = None
    write_excel = True

    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, mz_name, tag, write_excel)


if __name__ == '__main__':
    main()
