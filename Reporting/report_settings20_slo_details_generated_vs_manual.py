import re
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    slo_dashboard_lookup = load_slo_dashboard_lookup(env, token)

    rows = []
    count_total = 0

    endpoint = '/api/v2/settings/objects'
    schema_ids = 'builtin:monitoring.slo'
    schema_ids_param = f'schemaIds={schema_ids}'
    raw_params = schema_ids_param + '&scopes=environment&fields=schemaId,value,Summary&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for settings_object in settings_object_list:
        items = settings_object.get('items', [])

        if items:
            for item in items:
                value = item.get('value')
                slo_summary = item.get('summary').replace('\\', '')
                name = value.get('name')
                metric_name = value.get('metricName')
                metric_expression = value.get('metricExpression')
                enabled = value.get('enabled')
                slo_filter = value.get('filter')

                if 'mzName' in slo_filter:
                    management_zone_name = re.sub('.*mzName\(', '', slo_filter).replace(')', '').replace('"', '')
                    management_zone_name = re.sub(',.*', '', management_zone_name)
                else:
                    management_zone_name = ''

                slo_type = 'UNKNOWN'
                if ' - Synthetic Availability (HTTP)' in name:
                    slo_type = 'HTTP'
                else:
                    if ' - Synthetic Availability (Browser)' in name:
                        slo_type = 'Browser'
                    else:
                        if ' - Service Errors' in name or ' - Service Performance' in name:
                            slo_type = 'Service'
                        else:
                            if ' - Host Availability' in name:
                                slo_type = 'Host'

                slo_dashboard_lookup_key = (management_zone_name, slo_type)

                print(slo_dashboard_lookup_key, slo_dashboard_lookup)

                slo_type = 'Manual'
                if slo_dashboard_lookup_key in slo_dashboard_lookup:
                    slo_type = 'Generated'

                rows.append((name, management_zone_name, slo_summary, metric_name, metric_expression, enabled, slo_type))

                count_total += 1

    rows = sorted(rows)
    report_name = 'SLO Definitions'
    report_writer.initialize_text_file(None)
    report_headers = ('Name', 'Management Zone Name', 'Summary', 'MetricName', 'MetricExpression', 'Enabled', 'SLO Type')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    write_strings(['Total SLO definitions: ' + str(count_total)])
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def load_slo_dashboard_lookup(env, token):
    rows = []

    count_total = 0

    endpoint = '/api/config/v1/dashboards'
    dashboards_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')

            if not entity_id.startswith('00000001-0000-0000-'):
                continue

            name = inner_dashboards_json.get('name')
            management_zone_name = name.split(' ')[0]

            dashboard_type = 'UNKNOWN'
            if entity_id.startswith('00000001-0000-0000-0000'):
                dashboard_type = 'HTTP'
            else:
                if entity_id.startswith('00000001-0000-0000-0001'):
                    dashboard_type = 'Browser'
                else:
                    if entity_id.startswith('00000001-0000-0000-0002'):
                        dashboard_type = 'Service'
                    else:
                        if entity_id.startswith('00000001-0000-0000-0003'):
                            dashboard_type = 'Host'

            rows.append((management_zone_name, dashboard_type))

            count_total += 1

    rows = sorted(rows)
    # report_name = 'Generated SLOs'
    # report_writer.initialize_text_file(None)
    # report_headers = ('ASN', 'SLO Type')
    # report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    # report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    # write_strings(['Generated SLOs/Dashboards: ' + str(count_total)])
    # report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    # report_writer.write_html(None, report_name, report_headers, rows)

    print(f'Loaded {count_total} SLO Dashboards to lookup list')

    return rows


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
