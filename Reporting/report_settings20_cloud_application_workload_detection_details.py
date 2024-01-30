# https://*.live.dynatrace.com/ui/settings/builtin:process-group.cloud-application-workload-detection?gtf=-2h&gf=all

import urllib.parse

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

    schema_id = 'builtin:process-group.cloud-application-workload-detection'

    endpoint = '/api/v2/settings/objects'
    raw_params = f'schemaIds={schema_id}&fields=value,scope&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for settings_object in settings_object_list:
        items = settings_object.get('items')
        for item in items:
            if not summary_mode:
                value = item.get('value')
                kubernetes = value.get('kubernetes')
                kubernetes_enabled = kubernetes.get('enabled')
                if kubernetes_enabled:
                    summary.append(f'{schema_id} is enabled, which is required for the "Monitor Kubernetes namespaces, services, workloads and pods" flag to be enabled for Kubernetes Monitoring')
                else:
                    summary.append(f'{schema_id} is disabled.  It must be enabled for the "Monitor Kubernetes namespaces, services, workloads and pods" flag to be enabled for Kubernetes Monitoring')

                rows.append([schema_id, kubernetes_enabled])

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Cloud App Workload Detection'
        report_writer.initialize_text_file(None)
        report_headers = ['Key Request', 'Scope']
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
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
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
