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

    endpoint = '/api/config/v1/kubernetes/credentials'
    params = ''
    kubernetes_credentials_json_list = dynatrace_api.get(env, token, endpoint, params)

    events_not_enabled = []

    for kubernetes_credentials_json in kubernetes_credentials_json_list:
        inner_kubernetes_credentials_json_list = kubernetes_credentials_json.get('values')
        for inner_kubernetes_credentials_json in inner_kubernetes_credentials_json_list:
            entity_id = inner_kubernetes_credentials_json.get('id')
            name = inner_kubernetes_credentials_json.get('name')
            endpoint_url = inner_kubernetes_credentials_json.get('endpointUrl')

            endpoint = '/api/config/v1/kubernetes/credentials/' + entity_id
            params = ''
            details = dynatrace_api.get(env, token, endpoint, params)[0]

            events_integration_enabled = details.get('eventsIntegrationEnabled')

            if not events_integration_enabled:
                events_not_enabled.append(name)

            if not summary_mode:
                rows.append((name, entity_id, str(endpoint_url), str(events_integration_enabled)))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' kubernetes clusters currently configured.')

    if count_total > 0:
        if len(events_not_enabled) > 0:
            events_not_enabled_string = str(events_not_enabled)
            events_not_enabled_string = events_not_enabled_string.replace('[', '')
            events_not_enabled_string = events_not_enabled_string.replace(']', '')
            events_not_enabled_string = events_not_enabled_string.replace("'", "")
            summary.append('The following ' + str(len(events_not_enabled)) + ' clusters do not have events integration enabled: ' + events_not_enabled_string)
        else:
            summary.append('All kubernetes clusters have events integration enabled as per expectations.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Kubernetes Credentials'
        report_writer.initialize_text_file(None)
        report_headers = ('id', 'name', 'endpointUrl', 'eventsIntegrationEnabled')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Kubernetes Clusters: ' + str(count_total)])
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
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
