import os
import requests
import time
import urllib.parse


def process(env, token, print_mode):
    detected_host_name_list = []

    hosts = get_hosts(env, token)
    for entities in hosts:
        total_count = int(entities.get('totalCount'))
        if total_count > 0:
            host_entities = entities.get('entities')
            for host_json in host_entities:
                display_name = host_json.get('displayName', '')
                detected_name = host_json.get('properties').get('detectedName', '')
                # print(f'{detected_name}: {display_name}')
                if detected_name == '':
                    detected_host_name_list.append(display_name.lower())
                else:
                    detected_host_name_list.append(detected_name.lower())

    host_name_list = remove_duplicates(sorted(detected_host_name_list))

    if print_mode:
        for host_name in host_name_list:
            print(host_name)

    return host_name_list


def get_hosts(env, token):
    # print(f'get_entity_types({env}, {token})')
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=500&entitySelector=type(HOST)&fields=+properties.detectedName'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    hosts = get_rest_api_json(env, token, endpoint, params)
    return hosts


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    try:
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    except ConnectionError:
        print('Sleeping 30 seconds before retrying due to connection error...')
        time.sleep(30)
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})

    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    json_data = resp.json()

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json_data) is list:
        # DEBUG:
        # print(json_data)
        return json_data

    json_list = [json_data]
    next_page_key = json_data.get('nextPageKey')

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

        json_data = resp.json()
        # print(json_data)

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def main():
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

    print(f'Environment Name: {env_name}')
    print(f'Environment:      {env}')
    print(f'Token:            {masked_token}')

    print('')
    print('Hosts monitored by OneAgent')

    process(env, token, True)


if __name__ == '__main__':
    main()
