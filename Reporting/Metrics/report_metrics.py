import sys
import urllib

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    endpoint = '/api/v2/metrics'
    raw_params = 'pageSize=500&fields=+created'
    # raw_params = 'pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    metrics_json_list = dynatrace_api.get(env, token, endpoint, params)
    print('metric_id' + '|' + 'displayName' + '|' + 'created')
    # print('metric_id' + '|' + 'displayName')
    # print('metricId')
    for metrics_json in metrics_json_list:
        inner_metrics_json_list = metrics_json.get('metrics')
        for inner_metrics_json in inner_metrics_json_list:
            metric_id = inner_metrics_json.get('metricId')
            display_name = inner_metrics_json.get('displayName')
            created = inner_metrics_json.get('created')
            # https://www.epochconverter.com/
            # Use Epoch timestamp in milliseconds format
            # if created and created > 1668574800000:
            #     print(metric_id + '|' + display_name + '|' + str(created))
            # if created and created > 1000000000000:
            print(metric_id + '|' + display_name + '|' + str(created))
            # print(metric_id + '|' + display_name)
            # print(metric_id)
    print('Done!')


def run():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token)


def main(arguments):
    usage = '''
    metrics_report.py: Report Metrics 

    Usage:    metrics_report.py <tenant/environment URL> <token>
    Examples: metrics_report.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123
              metrics_report.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123
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

