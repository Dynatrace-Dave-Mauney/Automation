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

    endpoint = '/api/v2/settings/schemas'
    params = ''
    settings_json_list = dynatrace_api.get(env, token, endpoint, params)

    for settings_json in settings_json_list:
        inner_settings_json_list = settings_json.get('items')
        for inner_settings_json in inner_settings_json_list:
            schema_id = inner_settings_json.get('schemaId')
            display_name = inner_settings_json.get('displayName')
            latest_schema_version = inner_settings_json.get('latestSchemaVersion')
            endpoint = '/api/v2/settings/objects'
            raw_params = f'schemaIds={schema_id}&scopes=environment&fields=objectId,value&pageSize=500'
            params = urllib.parse.quote(raw_params, safe='/,&=')
            settings_object = dynatrace_api.get(env, token, endpoint, params)[0]
            items = settings_object.get('items')
            count_objects = 0
            for item in items:
                object_id = item.get('objectId')
                value = str(item.get('value'))
                value = value.replace('{', '')
                value = value.replace('}', '')
                value = value.replace("'", "")
                if not summary_mode:
                    rows.append((schema_id, latest_schema_version, display_name, value, object_id))
                count_objects += 1

            summary.append('Total ' + schema_id + ' Objects: ' + str(count_objects))

            count_total += 1

    # It just happens that the whole summary can be sorted in this particular case.
    summary = sorted(summary)

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Environment Settings 2.0'
        report_writer.initialize_text_file(None)
        report_headers = ('Schema ID', 'Latest Schema Version', 'Display Name', 'Value', 'Object ID')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Schemas: ' + str(count_total)])
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
