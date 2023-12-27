from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []

    count_total = 0
    count_shared = 0
    count_preset = 0
    count_dynatrace_owned = 0

    endpoint = '/api/config/v1/dashboards'
    dashboards_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')
            name = inner_dashboards_json.get('name')
            owner = inner_dashboards_json.get('owner')

            endpoint = '/api/config/v1/dashboards'
            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            dashboard = r.json()
            dashboard_metadata = dashboard.get('dashboardMetadata')
            shared = dashboard_metadata.get('shared', False)
            preset = dashboard_metadata.get('preset', False)

            if not summary_mode:
                rows.append((name, entity_id, owner, str(shared), str(preset)))

            count_total += 1
            if shared:
                count_shared += 1
            if preset:
                count_preset += 1
            if owner == 'Dynatrace':
                count_dynatrace_owned += 1

    summary.append('There are ' + str(count_total) + ' dashboards currently defined.  ' +
                   str(count_shared) + ' are currently shared. ' + str(count_preset) + ' are defined as preset. ' + str(count_dynatrace_owned) + ' were created by Dynatrace.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Dashboards (Extended Details)'
        report_writer.initialize_text_file(None)
        report_headers = ('name', 'id', 'owner', 'shared', 'preset')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Dashboards: ' + str(count_total)])
        write_strings(['Shared Dashboards: ' + str(count_shared)])
        write_strings(['Shared Dashboards: ' + str(count_preset)])
        write_strings(['Dynatrace Created Dashboards: ' + str(count_dynatrace_owned)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
