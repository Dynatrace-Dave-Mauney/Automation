import json

from requests.exceptions import HTTPError

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    console_tuple_list = []
    worksheet_tuple_list = []
    html_tuple_list = []
    tuple_lists = [console_tuple_list, worksheet_tuple_list, html_tuple_list]

    headers, rows = process_connectivity_info(env, token)
    append_report('Connectivity', headers, rows, tuple_lists)
    headers, rows = process_versions(env, token)
    append_report('OneAgent Versions', headers, rows, tuple_lists)
    headers, rows = process_latest_version(env, token)
    append_report('Latest OneAgent Versions', headers, rows, tuple_lists)
    headers, rows = process_active_gate_endpoints(env, token)
    append_report('ActiveGate Endpoints', headers, rows, tuple_lists)

    # Write Reports
    report_writer.initialize_text_file(None)
    report_writer.write_console_group(console_tuple_list)
    report_writer.write_text_group(None, console_tuple_list)
    report_writer.write_xlsx_worksheets(None, worksheet_tuple_list)
    report_writer.write_html_group(None, html_tuple_list)


def append_report(report_name, headers, rows, tuple_lists):
    console_tuple_list, worksheet_tuple_list, html_tuple_list = tuple_lists
    console_tuple_list.append((report_name, headers, rows, '|'))
    worksheet_tuple_list.append((report_name, headers, rows, None, None))
    html_tuple_list.append((report_name, headers, rows))


def process_connectivity_info(env, token):
    rows = []
    endpoint = '/api/v1/deployment/installer/agent/connectioninfo'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    connection_info_json = r.json()
    communication_endpoints = connection_info_json.get('communicationEndpoints')

    headers = ['Communication Endpoint']
    for communication_endpoint in communication_endpoints:
        rows.append([communication_endpoint])

    return headers, sorted(rows)


def process_active_gate_endpoints(env, token):
    rows = []
    endpoint = '/api/v1/deployment/installer/agent/connectioninfo/endpoints'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    active_gate_endpoints = r.text
    headers = (['ActiveGate Endpoint'])
    active_gate_endpoint_list = active_gate_endpoints.split(';')
    for active_gate_endpoint in active_gate_endpoint_list:
        print(active_gate_endpoint)
        rows.append([active_gate_endpoint])

    return headers, sorted(rows)


def process_versions(env, token):
    rows = []
    os_type_list = ['windows', 'unix', 'aix', 'solaris', 'zos']
    # installer_type_list = ['default', 'default-unattended', 'mainframe', 'paas', 'paas-sh']
    installer_type_list = ['default', 'default-unattended', 'paas', 'paas-sh']

    headers = (['OS Type', 'Installer Type', 'Available Version'])
    for os_type in os_type_list:
        for installer_type in installer_type_list:
            endpoint = f'/api/v1/deployment/installer/agent/versions/{os_type}/{installer_type}'
            try:
                r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token, handle_exceptions=False)
                agent_version_json = r.json()
                available_versions = agent_version_json.get('availableVersions')
                if available_versions:
                    for available_version in available_versions:
                        rows.append([os_type, installer_type, available_version])
                        print(os_type, installer_type, available_version)
            except HTTPError as e:
                handle_http_exception(e, f'{env}{endpoint}')

    return headers, sorted(rows)


def process_latest_version(env, token):
    rows = []
    os_type_list = ['windows', 'unix', 'aix', 'solaris', 'zos']
    installer_type_list = ['default', 'default-unattended', 'mainframe', 'paas', 'paas-sh']

    headers = (['OS Type', 'Installer Type', 'Latest Version'])
    for os_type in os_type_list:
        for installer_type in installer_type_list:
            endpoint = f'/api/v1/deployment/installer/agent/{os_type}/{installer_type}/latest/metainfo'
            try:
                r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token, handle_exceptions=False)
                agent_version_json = r.json()
                latest_version = agent_version_json.get('latestAgentVersion')
                if latest_version:
                    rows.append([os_type, installer_type, latest_version])
            except HTTPError as e:
                handle_http_exception(e, f'{env}{endpoint}')

    return headers, sorted(rows)


def handle_http_exception(e, url):
    if "[404]" not in str(e.response):
        print(f'HTTPError: URL: "{url}" Response: "{e.response}"')
        # Want to log 404s?  Add else statment and uncomment:
        # print(f'HTTPError (404 - Not Found): URL: {url}')


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting Deployment'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
