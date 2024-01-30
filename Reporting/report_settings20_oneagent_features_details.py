import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []

    endpoint = '/api/v2/settings/objects'
    schema_ids = 'builtin:oneagent.features'
    schema_ids_param = f'schemaIds={schema_ids}'
    raw_params = schema_ids_param + '&scopes=environment&fields=schemaId,value,Summary&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for settings_object in settings_object_list:
        items = settings_object.get('items', [])
        for item in items:
            value = item.get('value')
            summary = item.get('summary').replace('\\', '')
            enabled = value.get('enabled')
            rows.append((summary, enabled))

    rows = sorted(rows)
    report_name = 'OneAgent Features'
    report_writer.initialize_text_file(None)
    report_headers = ('Summary', 'Enabled')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


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
