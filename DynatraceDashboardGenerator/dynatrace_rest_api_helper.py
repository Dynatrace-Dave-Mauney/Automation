#
# Access the Dynatrace REST API for any endpoint, and handle pagination and rate limits (in the future) as needed.
#

# TODO:
# 1. Use params dictionaries only.  No string params.  For urlencoding...
# 2. Account for Rate Limits

import requests
import sys


def get_rest_api_json(url, token, endpoint, params):
    print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200:
        print('REST API Call Failed!')
        print(f'GET {full_url} {resp.status_code} - {resp.reason}')
        exit(1)

    json = resp.json()
    json_list = [json]
    next_page_key = json.get('nextPageKey')

    while next_page_key is not None:
        # next_page_key = next_page_key.replace('=', '%3D') # Ths does NOT help.  Also, equals are apparently fine in params.
        print(f'next_page_key: {next_page_key}')
        params = {'nextPageKey': next_page_key}
        full_url = url + endpoint
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
        print(resp.url)

        if resp.status_code != 200:
            print('Paginated REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            exit(1)

        json = resp.json()
        print(json)

        next_page_key = json.get('nextPageKey')
        json_list.append(json)

    return json_list


def test_metrics(url, token):
    endpoint = '/api/v2/metrics'
    params = '?pageSize=1000&fields=+displayName,+description,+unit,+aggregationTypes,' \
             '+defaultAggregation,+dimensionDefinitions,+transformations,+entityType'
    metrics = get_rest_api_json(url, token, endpoint, params)
    print(metrics)


def test_entity_types(url, token):
    endpoint = '/api/v2/entityTypes'
    params = '?pageSize=500'
    entity_types = get_rest_api_json(url, token, endpoint, params)
    print(entity_types)


def process(arguments):
    # Assume tenant/environment URL followed by Token
    url = arguments[1]
    token = arguments[2]

    test_metrics(url, token)
    test_entity_types(url, token)

    print('url: ' + url)
    print('token: ' + token[0:31] + '.*' + ' (masked for security)')


def main(arguments):
    help_text = '''
    dynatrace_rest_api_helper.py assists with calling the Dynatrace REST API from other Python modules.
    You can test it out by running it with a tenant and token.

    Usage:    dynatrace_rest_api_helper.py <tenant/environment URL> <token>
    Examples: dynatrace_rest_api_helper.py https://TENANTID.live.dynatrace.com <TOKEN>>
              dynatrace_rest_api_helper.py https://TENANTID.dynatrace-managed.com/e/<ENV_ID> <TOKEN>
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
    elif arguments[1] in ['-v', '--version']:
        print('1.0')
    else:
        if len(arguments) == 3:
            process(arguments)
        else:
            print(help_text)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
