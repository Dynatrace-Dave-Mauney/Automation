from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


friendly_type_name = {'log': 'Log Monitoring', 'mobile': 'Mobile/Custom Applications', 'service': 'Services', 'synthetic': 'Synthetics', 'rum': 'Web Applications'}


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []
    count_total = 0

    type_rows, type_summary, type_total = process_type(env, token, summary_mode, 'mobile')
    rows.extend(type_rows)
    summary.extend(type_summary)
    count_total += type_total

    type_rows, type_summary, type_total = process_type(env, token, summary_mode, 'service')
    rows.extend(type_rows)
    summary.extend(type_summary)
    count_total += type_total

    type_rows, type_summary, type_total = process_type(env, token, summary_mode, 'synthetic')
    rows.extend(type_rows)
    summary.extend(type_summary)
    count_total += type_total

    type_rows, type_summary, type_total = process_type(env, token, summary_mode, 'rum')
    rows.extend(type_rows)
    summary.extend(type_summary)
    count_total += type_total

    # This one does not work when log v2 is enabled...
    # type_rows, type_summary, type_total = process_type(env, token, summary_mode, 'log')
    # rows.extend(type_rows)
    # summary.extend(type_summary)
    # count_total += type_total

    summary.append('There are ' + str(count_total) + ' calcualated metrics currently defined.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Calculated Metrics'
        report_writer.initialize_text_file(None)
        report_headers = ('name', 'entityId', 'type')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Calculated Metrics: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def process_type(env, token, summary_mode, entity_type):
    rows = []
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/calculatedMetrics/' + entity_type
    calculated_metrics_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for calculated_metrics_json in calculated_metrics_json_list:
        inner_calculated_metrics_json_list = calculated_metrics_json.get('values')
        for inner_calculated_metrics_json in inner_calculated_metrics_json_list:
            entity_id = inner_calculated_metrics_json.get('id')
            name = inner_calculated_metrics_json.get('name')

            if not summary_mode:
                rows.append((name, entity_id, friendly_type_name[entity_type]))

            count_total += 1

    # if not summary_mode:
    #     print('Total Calculated Metrics - ' + friendly_type_name[entity_type] + ': ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' calculated metrics for ' + friendly_type_name[entity_type] + ' currently defined.')

    return rows, summary, count_total


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
