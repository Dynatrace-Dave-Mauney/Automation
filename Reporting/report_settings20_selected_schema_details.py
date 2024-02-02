import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


include_list = [
    'builtin:anomaly-detection.metric-events',
    'builtin:logmonitoring.schemaless-log-metric',
    'builtin:logmonitoring.log-events',
    'builtin:logmonitoring.log-storage-settings',
]


def process(env, token):
    rows = []

    endpoint = '/api/v2/settings/objects'
    raw_params = 'scopes=environment&fields=schemaId,value&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for settings_object in settings_object_list:
        items = settings_object.get('items')
        for item in items:
            schema_id = item.get('schemaId')
            row = format_schema(schema_id, item)
            if row:
                rows.append(row)

    rows = sorted(rows)
    report_name = 'Settings 2.0'
    report_writer.initialize_text_file(None)
    report_headers = ('Setting', 'Values of Interest', 'Enabled')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def format_schema(schema_id, json_data):
    if schema_id == 'builtin:anomaly-detection.metric-events':
        value = json_data.get('value')
        event_template = value.get('eventTemplate')
        enabled = value.get('enabled')
        title = event_template.get('title')
        return ['Metric Event', title, enabled]

    if schema_id == 'builtin:logmonitoring.schemaless-log-metric':
        value = json_data.get('value')
        enabled = value.get('enabled')
        key = value.get('key')
        return ['Log Metric', key, enabled]

    if schema_id == 'builtin:logmonitoring.log-events':
        value = json_data.get('value')
        enabled = value.get('enabled')
        summary = value.get('summary')
        return ['Log Event', summary, enabled]

    if schema_id == 'builtin:logmonitoring.log-storage-settings':
        value = json_data.get('value')
        enabled = value.get('enabled')
        config_item_title = value.get('config-item-title')
        return ['Log Storage Setting', config_item_title, enabled]

    # import json
    # print(schema_id)
    # print(json.dumps(json_data, indent=4, sort_keys=False))

    return None


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
