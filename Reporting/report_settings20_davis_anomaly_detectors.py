import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


include_list = [
    'builtin:davis.anomaly-detectors',
]


def process(env, token):
    rows = []

    endpoint = '/api/v2/settings/objects'
    raw_params = 'scopes=environment&fields=schemaId,objectId,createdBy,author,owner,externalId,value&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for settings_object in settings_object_list:
        items = settings_object.get('items')
        for item in items:
            schema_id = item.get('schemaId')
            if schema_id in include_list:
                row = format_schema(schema_id, item)
                if row:
                    rows.append(row)

    rows = sorted(rows)
    report_name = 'Settings 2.0'
    report_writer.initialize_text_file(None)
    report_headers = ('Title', 'Enabled', 'Basis', 'Sliding Window', 'Object ID')
    # report_headers = ('Selected Objects')
    # report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    # report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def format_schema(schema_id, json_data):
    if schema_id == 'builtin:davis.anomaly-detectors':
        value = json_data.get('value')
        enabled = value.get('enabled')
        title = value.get('title')

        analyzer = value.get('analyzer')
        input = analyzer.get('input')

        sliding_window = '0'
        basis = 'Unknown'

        for i in input:
            if 'query' in str(i):
                query = i.get('value')

                if 'timeseries' in query and 'makeTimeseries' not in query:
                    basis = 'Metrics'
                else:
                    if 'fetch' in query:
                        if 'logs' in query:
                            basis = 'Logs'
                        else:
                            if 'spans' in query:
                                basis = 'Spans'
                            else:
                                basis = 'Unknown'

            if 'slidingWindow' in str(i):
                sliding_window = i.get('value')

        if str(title).startswith('Team_Thor - '):
            object_id = json_data.get('objectId')
            return [title, enabled, basis, int(sliding_window), object_id]

    return None


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Sandbox'
    #
    # env_name_supplied = 'Upper'
    # env_name_supplied = 'Lower'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
