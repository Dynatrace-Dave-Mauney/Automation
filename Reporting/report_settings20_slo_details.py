import re
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    customer_specific_management_zone_names = environment.get_configuration('report_settings20_slo_details.management_zone_names')

    rows = []
    summary = []

    count_total = 0

    endpoint = '/api/v2/settings/objects'
    schema_ids = 'builtin:monitoring.slo'
    schema_ids_param = f'schemaIds={schema_ids}'
    raw_params = schema_ids_param + '&scopes=environment&fields=schemaId,value,Summary&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object_list = dynatrace_api.get(env, token, endpoint, params)

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
                    if customer_specific_management_zone_names:
                        management_zone_name = customer_specific_management_zone_names.get(name, '')
                    if management_zone_name == '':
                        print(f'Management zone missing for {name}: {slo_filter}: {item}')

                if not summary_mode:
                    rows.append((name, management_zone_name, slo_summary, metric_name, metric_expression, enabled))

                count_total += 1

    summary.append('There are ' + str(count_total) + ' SLOs currently defined.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'SLO Definitions'
        report_writer.initialize_text_file(None)
        report_headers = ('Name', 'Management Zone Name', 'Summary', 'MetricName', 'MetricExpression', 'Enabled')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total SLO definitions: ' + str(count_total)])
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
