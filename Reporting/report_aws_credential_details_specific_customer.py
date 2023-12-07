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
    count_with_supporting_services = 0
    count_without_supporting_services = 0

    counts_supporting_service = {}
    counts_supporting_service_metric_details = {}

    endpoint = '/api/config/v1/aws/credentials'
    aws_credentials_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for aws_credentials_json in aws_credentials_json_list:
        entity_id = aws_credentials_json.get('id')
        name = aws_credentials_json.get('name')

        endpoint = '/api/config/v1/aws/credentials/' + entity_id
        params = ''
        r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
        aws_credentials = r.json()
        supporting_services = aws_credentials.get('supportingServicesToMonitor')

        if supporting_services:
            count_with_supporting_services += 1
            for supporting_service in supporting_services:
                supporting_service_name = supporting_service.get('name')
                counts_supporting_service[supporting_service_name] = counts_supporting_service.get(supporting_service_name, 0) + 1
                monitored_metrics = supporting_service.get('monitoredMetrics')
                for monitored_metric in monitored_metrics:
                    supporting_service_metric_name = monitored_metric.get('name')
                    supporting_service_metric_statistic = monitored_metric.get('statistic')
                    supporting_service_metric_dimensions_str = sort_and_stringify_list_items(monitored_metric.get('dimensions'))
                    supporting_service_metric_details = supporting_service_name + '|' + supporting_service_metric_name + '|' + supporting_service_metric_statistic + '|' + supporting_service_metric_dimensions_str
                    counts_supporting_service_metric_details[supporting_service_metric_details] = counts_supporting_service_metric_details.get(supporting_service_metric_details, 0) + 1
        else:
            count_without_supporting_services += 1

        if not summary_mode:
            rows.append((name, entity_id))

        count_total += 1

    counts_supporting_service_str = sort_and_stringify_dictionary_items(counts_supporting_service)
    counts_supporting_service_metric_details_str = sort_and_stringify_dictionary_items(counts_supporting_service_metric_details)

    summary.append('There are ' + str(count_total) + ' AWS accounts currently configured.')
    if count_total > 0:
        summary.append('Accounts with Supporting Service monitoring: ' + str(count_with_supporting_services) + '.')
        summary.append('Accounts without Supporting Service monitoring: ' + str(count_without_supporting_services) + '.')
    if count_with_supporting_services > 0:
        summary.append('The Supporting Service breakdown is ' + counts_supporting_service_str + '.')
        summary.append('The Supporting Service metric breakdown is ' + counts_supporting_service_metric_details_str + '.')

    if not summary_mode:
        report_name = 'AWS Credentials Sup Svc Details'
        report_writer.initialize_text_file(None)
        report_headers = ('Name', 'ID')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total AWS Accounts:                             ' + str(count_total)])
        write_strings(['Accounts with Supporting Service monitoring:    ' + str(count_with_supporting_services)])
        write_strings(['Accounts without Supporting Service monitoring: ' + str(count_without_supporting_services)])
        write_strings(['Supporting Service Counts:                      ' + str(counts_supporting_service_str)])
        write_strings(['Supporting Service Metric Counts:               ' + str(counts_supporting_service_metric_details_str)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def sort_and_stringify_dictionary_items(any_dict):
    dict_str = str(sorted(any_dict.items()))
    dict_str = dict_str.replace('[', '')
    dict_str = dict_str.replace(']', '')
    dict_str = dict_str.replace('), (', '~COMMA~')
    dict_str = dict_str.replace('(', '')
    dict_str = dict_str.replace(')', '')
    dict_str = dict_str.replace(',', ':')
    dict_str = dict_str.replace('~COMMA~', ', ')
    dict_str = dict_str.replace("'", "")
    return dict_str


def sort_and_stringify_list_items(any_list):
    list_str = str(sorted(any_list))
    list_str = list_str.replace('[', '')
    list_str = list_str.replace(']', '')
    list_str = list_str.replace("'", "")
    list_str = list_str.replace(' ', '')
    return list_str


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
