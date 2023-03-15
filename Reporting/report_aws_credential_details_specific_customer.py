from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    count_with_supporting_services = 0
    count_without_supporting_services = 0

    counts_supporting_service = {}
    counts_supporting_service_metric_details = {}

    endpoint = '/api/config/v1/aws/credentials'
    params = ''
    aws_credentials_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name')

    for aws_credentials_json in aws_credentials_json_list:
        entity_id = aws_credentials_json.get('id')
        name = aws_credentials_json.get('name')

        endpoint = '/api/config/v1/aws/credentials/' + entity_id
        params = ''
        aws_credentials = dynatrace_api.get(env, token, endpoint, params)[0]
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

        if print_mode:
            print(entity_id + '|' + name)

        count_total += 1

    counts_supporting_service_str = sort_and_stringify_dictionary_items(counts_supporting_service)
    counts_supporting_service_metric_details_str = sort_and_stringify_dictionary_items(counts_supporting_service_metric_details)

    if print_mode:
        print('Total AWS Accounts:        ' + str(count_total))
        print('Accounts with Supporting Service monitoring: ' + str(count_with_supporting_services))
        print('Accounts without Supporting Service monitoring: ' + str(count_without_supporting_services))
        print('Supporting Service Counts: ' + counts_supporting_service_str)
        print('Supporting Service Metric Counts: ' + counts_supporting_service_metric_details_str)

    summary.append('There are ' + str(count_total) + ' AWS accounts currently configured.')
    if count_total > 0:
        summary.append('Accounts with Supporting Service monitoring: ' + str(count_with_supporting_services) + '.')
        summary.append('Accounts without Supporting Service monitoring: ' + str(count_without_supporting_services) + '.')
    if count_with_supporting_services > 0:
        summary.append('The Supporting Service breakdown is ' + counts_supporting_service_str + '.')
        summary.append('The Supporting Service metric breakdown is ' + counts_supporting_service_metric_details_str + '.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


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
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
