#
# Access the Dynatrace REST API for any endpoint, and handle pagination and rate limits (in the future) as needed.
#

# TODO:
# 1. Use params dictionaries only.  No string params.  For urlencoding...
# 2. Account for Rate Limits

import requests
import sys
import urllib.parse


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    json = resp.json()

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json) is list:
        # DEBUG:
        # print(json)
        return json

    json_list = [json]
    next_page_key = json.get('nextPageKey')

    while next_page_key is not None:
        # print(f'next_page_key: {next_page_key}')
        params = {'nextPageKey': next_page_key}
        full_url = url + endpoint
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
        # print(resp.url)

        if resp.status_code != 200:
            print('Paginated REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            exit(1)

        json = resp.json()
        # print(json)

        next_page_key = json.get('nextPageKey')
        json_list.append(json)

    return json_list


def test_metrics(url, token):
    endpoint = '/api/v2/metrics'
    raw_params = 'pageSize=1000&fields=+displayName,+description,+unit,+aggregationTypes,+defaultAggregation,+dimensionDefinitions,+transformations,+entityType'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    metrics = get_rest_api_json(url, token, endpoint, params)
    print(metrics)


def test_entity_types(url, token):
    endpoint = '/api/v2/entityTypes'
    raw_params = 'pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entity_types = get_rest_api_json(url, token, endpoint, params)
    print(entity_types)


def test_entity_type_host(url, token):
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=500&entitySelector= type(HOST)&fields=+properties.monitoringMode,+properties.state,+toRelationships'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    hosts = get_rest_api_json(url, token, endpoint, params)
    print(hosts)
    for entities in hosts:
        total_count = int(entities.get('totalCount'))
        if total_count > 0:
            host_entities = entities.get('entities')
            for host in host_entities:
                print(host)


def process(arguments):
    # Assume tenant/environment URL followed by Token
    url = arguments[1]
    token = arguments[2]

    # test_metrics(url, token)
    # test_entity_types(url, token)
    test_entity_type_host(url, token)

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
