import os
import requests


def process(env, token):
    count_total = 0

    endpoint = '/api/config/v1/managementZones'
    params = ''
    management_zones_json_list = get_rest_api_json(env, token, endpoint, params)

    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        # for inner_management_zones_json in inner_management_zones_json_list:
        for _ in inner_management_zones_json_list:
            # id = inner_management_zones_json.get('id')
            # name = inner_management_zones_json.get('name')
            count_total += 1

    # print('Total Management Zones: ' + str(count_total))

    return count_total


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
        # next_page_key = next_page_key.replace('=', '%3D') # Ths does NOT help.  Also, equals are apparently fine in params.
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


def main():
    print('Management Zone Counts by Tenant')
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'
    total = process(env, token)
    print(env_name + ' ' + str(total))
    grand_total = total

    env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'
    total = process(env, token)
    print(env_name + ' ' + str(total))
    grand_total += total

    env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'
    total = process(env, token)
    print(env_name + ' ' + str(total))
    grand_total += total

    print('Grand Total: ' + str(grand_total))


if __name__ == '__main__':
    main()
