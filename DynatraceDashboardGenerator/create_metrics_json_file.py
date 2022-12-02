#
# Save metrics from Dynatrace REST API to a file in JSON format.
#

from dynatrace_rest_api_helper import get_rest_api_json
import json
import sys


def get_metrics(url, token):
    # print(f'get_metrics({url}, {token}')
    endpoint = '/api/v2/metrics'
    params = '?pageSize=1000&fields=+displayName,+description,+unit,+aggregationTypes,' \
             '+defaultAggregation,+dimensionDefinitions,+transformations,+entityType'
    metrics = get_rest_api_json(url, token, endpoint, params)
    return metrics


def write_metrics_file(url, token):
    metrics = get_metrics(url, token)
    full_list = []
    for outer_dict in metrics:
        temp_list = outer_dict.get('metrics', [])
        full_list += temp_list

    json_string = json.dumps(full_list)
    # Custom pretty print logic:
    # 1. Add newline after opening brace of metrics list
    # 2. Add newline after each metric in list
    # 3. Add newline before closing brace of metrics list
    json_string = json_string.replace('[{"metricId":', '[\n{"metricId":')
    json_string = json_string.replace(', {"metricId":', ',\n{"metricId":')
    json_string = json_string.replace('}]}]', '}]}\n]')

    with open('metrics.json', 'w') as file:
        file.write(json_string)


def process(arguments):
    # Assume tenant/environment URL followed by Token
    url = arguments[1]
    token = arguments[2]

    print('url: ' + url)
    print('token: ' + token[0:4] + '******************' + ' (masked for security)')

    write_metrics_file(url, token)


def main(arguments):
    help_text = '''
    create_metrics_file.py creates a metrics.txt file for an environment

    Usage:    create_metrics_file.py <tenant/environment URL> <token>
    '''

    print('args' + str(arguments))
    if len(arguments) < 2:
        print(help_text)
        raise ValueError('Too few arguments!')
    if len(arguments) > 3:
        print(help_text)
        raise ValueError('Too many arguments!')
    if arguments[1] in ['-h', '--help']:
        print(help_text)
    elif arguments[1] in ['-v', '--metrics']:
        print('1.0')
    else:
        if len(arguments) == 3:
            process(arguments)
        else:
            print(help_text)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
