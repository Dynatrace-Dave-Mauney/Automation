# import json

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

report_name = 'Unmonitored OneAgents'
report_headers = ['Host Name', 'ID', 'Monitoring State', 'Detailed Monitoring State', 'Monitoring Enabled Setting']
xlsx_file_name = 'UnmonitoredOneAgents.xlsx'
html_file_name = 'UnmonitoredOneAgents.html'


def process(env, token):
    print(f'XLSX File: {xlsx_file_name}')
    print(f'HTML File: {html_file_name}')
    rows = []

    endpoint = '/api/v1/oneagents'
    params = 'relativeTime=2hours'
    oneagents_json_list = dynatrace_api.get(env, token, endpoint, params)

    for oneagents_json in oneagents_json_list:
        inner_oneagents_json_list = oneagents_json.get('hosts')
        for inner_oneagents_json in inner_oneagents_json_list:
            host_info = inner_oneagents_json.get('hostInfo')
            entity_id = host_info.get('entityId')
            display_name = host_info.get('displayName')
            availability_state = inner_oneagents_json.get('availabilityState')
            detailed_availability_state = inner_oneagents_json.get('detailedAvailabilityState')
            configured_monitoring_enabled = inner_oneagents_json.get('configuredMonitoringEnabled')

            if availability_state and availability_state != 'MONITORED':
                rows.append((display_name, entity_id, availability_state, detailed_availability_state, configured_monitoring_enabled))

    sorted_rows = sorted(rows)

    write_console(sorted_rows)
    write_xlsx(sorted_rows)
    write_html(sorted_rows)


def write_console(rows):
    delimiter = '|'
    report_writer.write_console(report_name, report_headers, rows, delimiter)


def write_xlsx(rows):
    header_format = None
    auto_filter = (2, 2)
    report_writer.write_xlsx(xlsx_file_name, report_name, report_headers, rows, header_format, auto_filter)


def write_html(rows):
    report_writer.write_html(html_file_name, report_name, report_headers, rows)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
