import datetime
import urllib

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []
    endpoint = '/api/v2/metrics'
    raw_params = 'pageSize=500&fields=+created'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    metrics_json_list = dynatrace_api.get(env, token, endpoint, params)
    for metrics_json in metrics_json_list:
        inner_metrics_json_list = metrics_json.get('metrics')
        for inner_metrics_json in inner_metrics_json_list:
            metric_id = inner_metrics_json.get('metricId')

            # To report specific metric types
            # if 'calc:service' not in metric_id:
            #    continue

            display_name = inner_metrics_json.get('displayName')
            created = inner_metrics_json.get('created')
            # https://www.epochconverter.com/
            # Use Epoch timestamp in milliseconds format
            # if created and created > 1668574800000:
            rows.append((metric_id, display_name, convert_epoch_in_milliseconds_to_local(created)))

    rows = sorted(rows)
    report_name = 'Metrics'
    report_writer.initialize_text_file(None)
    report_headers = ('ID', 'Display Name', 'Created')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def convert_epoch_in_milliseconds_to_local(epoch):
    if epoch is None or epoch == -1 or epoch == 0:
        return ''
    else:
        return datetime.datetime.fromtimestamp(epoch / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)


if __name__ == '__main__':
    main()
