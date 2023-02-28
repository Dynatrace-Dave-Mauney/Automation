#
# Compare links from Hub UI and API.
# Output is written to the console in pipe-delimited format, to an Excel spreadsheet and to an HTML page.
#

import os
import requests
import time
from bs4 import BeautifulSoup


def get_links_from_api(env, token):
    result = {}

    endpoint = '/api/v2/hub/items'
    params = ''
    hub_items_json_list = get_rest_api_json(env, token, endpoint, params)
    for hub_items_json in hub_items_json_list:
        inner_hub_items_json_list = hub_items_json.get('items')
        for inner_hub_items_json in inner_hub_items_json_list:
            hub_item_name = inner_hub_items_json.get('name')
            hub_item_documentation_link = inner_hub_items_json.get('documentationLink')
            hub_item_marketing_link = inner_hub_items_json.get('marketingLink')
            result[hub_item_name] = (hub_item_documentation_link, hub_item_marketing_link)

    return result


def get_links_from_ui():
    page = requests.get('https://www.dynatrace.com/hub/')
    soup = BeautifulSoup(page.text, 'html.parser')

    result = {}

    for link in soup.find_all('a'):
        title = link.get('title')
        if title:
            href = link.get('href')
            if href.startswith('/'):
                href = f'https://dynatrace.com{href}'
            result[title] = href

    return result


def compare(api_links, ui_links):
    api_keys = list(api_links.keys())
    ui_keys = list(ui_links.keys())

    all_keys = []

    all_keys.extend(api_keys)
    all_keys.extend(ui_keys)

    all_unique_keys = sorted(list(set(all_keys)))

    for key in all_unique_keys:
        api_link_tuple = api_links.get(key, (None, None))
        ui_link = ui_links.get(key)
        if ui_link == api_link_tuple[0]:
            match_description = 'Doc'
        else:
            if ui_link == api_link_tuple[1]:
                match_description = 'Mkt'
            else:
                match_description = 'N/A'
        if match_description == 'Doc':
            print(f'{key}:{match_description}')
            print(f'{key}:{ui_link}:{api_link_tuple}')


def build_fall_back_links(api_links, ui_links):
    api_keys = list(api_links.keys())
    ui_keys = list(ui_links.keys())

    all_keys = []

    all_keys.extend(api_keys)
    all_keys.extend(ui_keys)

    all_unique_keys = sorted(list(set(all_keys)))

    for key in all_unique_keys:
        api_link_tuple = api_links.get(key, (None, None))
        ui_link = ui_links.get(key)
        if ui_link:
            if not api_link_tuple[0] and not api_link_tuple[1]:
                print(f'{key}:{ui_link}')


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
    env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

    print(f'Environment Name: {env_name}')
    print(f'Environment:      {env}')
    print(f'Token:            {masked_token}')

    print('')
    print('Hub Summary')

    api_links = get_links_from_api(env, token)
    ui_links = get_links_from_ui()
    # compare(api_links, ui_links)
    build_fall_back_links(api_links, ui_links)

if __name__ == '__main__':
    main()

