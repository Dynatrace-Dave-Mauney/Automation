from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []

    endpoint = '/api/v1/oneagents'
    params = 'relativeTime=2hours'
    oneagents_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for oneagents_json in oneagents_json_list:
        inner_oneagents_json_list = oneagents_json.get('hosts')
        for inner_oneagents_json in inner_oneagents_json_list:
            host_info = inner_oneagents_json.get('hostInfo')
            entity_id = host_info.get('entityId')
            display_name = host_info.get('displayName')
            availability_state = inner_oneagents_json.get('availabilityState')
            detailed_availability_state = inner_oneagents_json.get('detailedAvailabilityState')
            configured_monitoring_enabled = inner_oneagents_json.get('configuredMonitoringEnabled')
            rows.append((display_name, entity_id, availability_state, detailed_availability_state, configured_monitoring_enabled))

    sorted_rows = sorted(rows)

    report_name = 'OneAgent Monitored States'
    report_headers = ['Host Name', 'ID', 'Monitoring State', 'Detailed Monitoring State', 'Monitoring Enabled Setting']

    report_writer.write_console(report_name, report_headers, sorted_rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, sorted_rows, header_format=None, auto_filter=(2, 2))
    report_writer.write_html(None, report_name, report_headers, sorted_rows)


def main():
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
    process(env, token)
    
    
if __name__ == '__main__':
    main()
