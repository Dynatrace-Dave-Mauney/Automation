import urllib

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

    endpoint = '/api/v2/metrics'
    raw_params = 'pageSize=500&fields=+created'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    metrics_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for metrics_json in metrics_json_list:
        inner_metrics_json_list = metrics_json.get('metrics')
        for inner_metrics_json in inner_metrics_json_list:
            metric_id = inner_metrics_json.get('metricId')

            # Report only SLO metric types
            if not metric_id.startswith('func:slo'):
                continue

            # Skip the derived SLO metric types
            if metric_id.startswith('func:slo.normalizedErrorBudget') or metric_id.startswith('func:slo.errorBudget'):
                continue

            # Check for no data points
            if no_data_points_for_metric(env, token, metric_id):
                display_name = inner_metrics_json.get('displayName')

                if not summary_mode:
                    rows.append((display_name, metric_id))

                count_total += 1

    summary.append('There are ' + str(count_total) + ' broken SLO metrics.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Broken SLO Metrics'
        report_writer.initialize_text_file(None)
        report_headers = ('Display Name', 'ID')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

        write_strings(summary)

    return summary


def no_data_points_for_metric(env, token, metric_id):
    endpoint = '/api/v2/metrics/query'
    metric_query_options = ':names:fold'
    from_time = 'now-2h'
    params = 'metricSelector=' + urllib.parse.quote(metric_id) + metric_query_options + '&from=' + from_time
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token, params=params)
    metrics_json = r.json()
    result_list = metrics_json.get('result')
    for result in result_list:
        data = result.get('data')
        if data:
            return False
        else:
            return True

    # There were no results if this line is reached
    return True


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)


if __name__ == '__main__':
    main()
