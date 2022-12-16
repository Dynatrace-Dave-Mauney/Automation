import os
import requests
import urllib.parse


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    count_monitored_entity_types_total = 0
    count_monitored_total = 0

    endpoint = '/api/v2/entityTypes'
    params = ''
    entities_json_list = get_rest_api_json(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name' + '|' + 'monitored_count')

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('types')
        for inner_entities_json in inner_entities_json_list:
            # print(inner_entities_json)
            entity_type = inner_entities_json.get('type')
            display_name = inner_entities_json.get('displayName')
            # if entity_type.startswith('cloud:aws'):
            #     print(entity_type + '|' + display_name)
            if True:
                endpoint = '/api/v2/entities'
                entity_selector = 'type(' + entity_type + ')'
                params = '&entitySelector=' + urllib.parse.quote(entity_selector)
                # print(params)
                entity_type_json_list = get_rest_api_json(env, token, endpoint, params)
                total_count = entity_type_json_list[0].get('totalCount')
                if total_count > 0:
                    print(entity_type + '|' + display_name + '|' + str(total_count))
                    count_monitored_entity_types_total += 1
                    count_monitored_total += total_count

            count_total += 1

    if print_mode:
        print('Total entities defined:       ' + str(count_total))
        print('Total entity types monitored: ' + str(count_monitored_entity_types_total))
        print('Total entities monitored:     ' + str(count_monitored_total))

    summary.append('There are ' + str(count_total) + ' entity types currently defined, ' + str(count_monitored_entity_types_total) + ' entity types being monitored and a total of ' + str(count_monitored_total) + ' entities being monitored.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
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

    process(env, token, True)


if __name__ == '__main__':
    main()
