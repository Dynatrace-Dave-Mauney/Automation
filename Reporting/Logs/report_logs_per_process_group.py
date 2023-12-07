import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token, mz_name, tag):
    rows = []
    endpoint = '/api/v2/entities'
    entity_selector_param = 'entitySelector=type(PROCESS_GROUP)'
    mz_name_param = f',mzName("{mz_name}")'
    tag_param = f',tag("{tag}")'

    raw_params = entity_selector_param
    if mz_name:
        raw_params += mz_name_param
    if tag:
        raw_params += tag_param

    params = urllib.parse.quote(raw_params, safe='/,=')
    process_group_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for process_group_json in process_group_json_list:
        inner_process_group_json_list = process_group_json.get('entities')
        for inner_process_group_json in inner_process_group_json_list:
            entity_id = inner_process_group_json.get('entityId')
            display_name = inner_process_group_json.get('displayName')
            rows.extend(process_pg(env, token, entity_id, display_name, mz_name, tag))

    sorted_rows = sorted(rows, key=lambda row: row[0].lower())

    report_name = 'Logs Per Process Group'
    report_headers = ('Process Group Name', 'Log File Path', 'Management Zone', 'Tag')

    report_writer.write_console(report_name, report_headers, sorted_rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, sorted_rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, sorted_rows, header_format=None, auto_filter=(0, len(report_headers)))
    report_writer.write_html(None, report_name, report_headers, sorted_rows)


def process_pg(env, token, process_group, display_name, mz_name, tag):
    rows = []
    endpoint = '/api/v1/entity/infrastructure/process-groups/' + process_group + '/logs'
    process_group_logs_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    for process_group_logs_json in process_group_logs_json_list:
        inner_process_group_logs_json_list = process_group_logs_json.get('logs')
        for inner_process_group_logs_json in inner_process_group_logs_json_list:
            path = inner_process_group_logs_json.get('path')
            rows.append((display_name, path, mz_name, tag))

    return rows


def main():
    mz_name = None
    tag = None
    # mz_name = 'HostGroup:Laptops'
    # tag = 'Tech:Jetty'
    # tag = 'Tech:Java'
    # tag = 'Tech:.NET'

    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token, mz_name, tag)


if __name__ == '__main__':
    main()
