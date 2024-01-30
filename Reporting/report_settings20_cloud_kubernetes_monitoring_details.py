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
    count_total = 0
    count_cloud_application_pipeline_enabled = 0
    count_pvc_monitoring_enabled = 0
    count_open_metrics_pipeline_enabled = 0
    count_open_metrics_builtin_enabled = 0
    count_event_processing_active = 0
    count_filter_events = 0

    schema_id = 'builtin:cloud.kubernetes.monitoring'

    endpoint = '/api/v2/settings/objects'
    raw_params = f'schemaIds={schema_id}&fields=value,scope&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for settings_object in settings_object_list:
        # print(settings_object)
        items = settings_object.get('items')
        for item in items:
            scope = item.get('scope')
            value = item.get('value')
            cloud_application_pipeline_enabled = value.get('cloudApplicationPipelineEnabled')
            pvc_monitoring_enabled = value.get('pvcMonitoringEnabled')
            open_metrics_pipeline_enabled = value.get('openMetricsPipelineEnabled')
            open_metrics_builtin_enabled = value.get('openMetricsBuiltinEnabled')
            event_processing_active = value.get('eventProcessingActive')
            filter_events = value.get('filterEvents')

            if not summary_mode:
                rows.append((scope, cloud_application_pipeline_enabled, pvc_monitoring_enabled, open_metrics_pipeline_enabled, open_metrics_builtin_enabled, event_processing_active, filter_events))

            if scope != 'environment':
                count_total += 1

            if cloud_application_pipeline_enabled:
                count_cloud_application_pipeline_enabled += 1

            if pvc_monitoring_enabled:
                count_pvc_monitoring_enabled += 1

            if open_metrics_pipeline_enabled:
                count_open_metrics_pipeline_enabled += 1

            if open_metrics_builtin_enabled:
                count_open_metrics_builtin_enabled += 1

            if event_processing_active:
                count_event_processing_active += 1

            if filter_events:
                count_filter_events += 1

    summary.append(f'There are {count_total} kubernetes cloud monitoring scopes currently configured, excluding the "environment" scope.')
    summary.append(f'{count_cloud_application_pipeline_enabled} kubernetes cloud monitoring scopes have "Cloud Application Pipeline" enabled.')
    summary.append(f'{count_pvc_monitoring_enabled} kubernetes cloud monitoring scopes have "Persistent Volume Claims" enabled.')
    summary.append(f'{count_open_metrics_pipeline_enabled} kubernetes cloud monitoring scopes have "Open Metrics Pipeline" enabled.')
    summary.append(f'{count_open_metrics_builtin_enabled} kubernetes cloud monitoring scopes have "Open Metrics Builtin Pipeline" enabled.')
    summary.append(f'{count_event_processing_active} kubernetes cloud monitoring scopes have "Event Processing" enabled.')
    summary.append(f'{count_filter_events} kubernetes cloud monitoring scopes have "Event Filtering" enabled.')
    # summary = sorted(summary)

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Cloud Kubernetes Monitoring'
        report_writer.initialize_text_file(None)
        report_headers = ['Scope', 'cloudApplicationPipelineEnabled', 'pvcMonitoringEnabled', 'openMetricsPipelineEnabled', 'openMetricsBuiltinEnabled', 'eventProcessingActive', 'filterEvents']
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
