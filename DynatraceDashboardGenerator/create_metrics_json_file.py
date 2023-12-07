#
# Save metrics from Dynatrace REST API to a file in JSON format.
#

import json
import sys

from Reuse import dynatrace_api


def get_metrics(env, token):
    # print(f'get_metrics({env}, {token}')
    endpoint = '/api/v2/metrics'
    params = '?pageSize=1000&fields=+displayName,+description,+unit,+aggregationTypes,' \
             '+defaultAggregation,+dimensionDefinitions,+transformations,+entityType'
    metrics = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
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
    print('token: ' + token[0:31] + '.*' + ' (masked for security)')

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
