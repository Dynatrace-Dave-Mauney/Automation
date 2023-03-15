import os
import requests
import sys
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    endpoint = '/api/v2/metrics/query'
    metric_schema_id = 'builtin:host.availability'
    metric_query_options = ':names:fold:default(0):sort(dimension("dt.entity.host.name",ascending))'
    # metric_schema_id = 'ext:tech.IBMMQ_OneAgent.Queue.OldestMessageAge'
    # metric_query_options = ':names:fold:default(0)'
    # metric_query_options = ''
    # from_time = 'now-72h'
    from_time = 'now-30m'
    entity_selector = 'type(HOST)'
    # entity_selector = 'type(PROCESS_GROUP_INSTANCE)'
    params = 'metricSelector=' + urllib.parse.quote(metric_schema_id) + metric_query_options + '&from=' + from_time + '&entitySelector=' + urllib.parse.quote(entity_selector)
    metrics_json_list = dynatrace_api.get(env, token, endpoint, params)
    # print(metrics_json_list)
    for metrics_json in metrics_json_list:
        result_list = metrics_json.get('result')
        for result in result_list:
            # metric_id = result.get('metricId')
            data = result.get('data')
            for datapoint in data:
                # print(datapoint)
                values = datapoint.get('values')[0]
                # if values <= 75:
                display_name = datapoint.get('dimensionMap').get('dt.entity.host.name').strip()
                # display_name = datapoint.get('dimensionMap').get('dt.entity.process_group_instance_name').strip()
                print(display_name + '|' + str(values))


def run():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')
    process(env, token)


def main(arguments):
    usage = '''
    query_metric.py: Query a metric 

    Usage:    query_metric.py <tenant/environment URL> <token>
    Examples: query_metric.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123
              query_metric.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123
    '''

    # print('args' + str(arguments))
    if len(arguments) == 1:
        run()
        exit()
    if len(arguments) < 2:
        print(usage)
        raise ValueError('Too few arguments!')
    if len(arguments) > 3:
        print(help)
        raise ValueError('Too many arguments!')
    if arguments[1] in ['-h', '--help']:
        print(help)
    elif arguments[1] in ['-v', '--version']:
        print('1.0')
    else:
        if len(arguments) == 3:
            process(arguments[1], arguments[2])
        else:
            print(usage)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
