import os
import requests
import time


def process_hub_categories(env, token):
    print('Hub Categories')
    print(f'id|name|description')
    endpoint = '/api/v2/hub/categories'
    params = ''
    hub_categories_json_list = get_rest_api_json(env, token, endpoint, params)
    for hub_categories_json in hub_categories_json_list:
        inner_hub_categories_json_list = hub_categories_json.get('items')
        for inner_hub_categories_json in inner_hub_categories_json_list:
            hub_category_id = inner_hub_categories_json.get('id')
            hub_category_name = inner_hub_categories_json.get('name')
            hub_category_description = inner_hub_categories_json.get('description')
            print(f'{hub_category_id}|{hub_category_name}|{hub_category_description}')


def process_hub_items(env, token, show_description_blocks):
    print('Hub items')
    print(f'id|name|description')
    endpoint = '/api/v2/hub/items'
    params = ''
    hub_items_json_list = get_rest_api_json(env, token, endpoint, params)
    for hub_items_json in hub_items_json_list:
        inner_hub_items_json_list = hub_items_json.get('items')
        for inner_hub_items_json in inner_hub_items_json_list:
            hub_item_type = inner_hub_items_json.get('type')
            hub_item_id = inner_hub_items_json.get('itemId')
            hub_item_name = inner_hub_items_json.get('name')
            hub_item_description = inner_hub_items_json.get('description')
            hub_item_tags = inner_hub_items_json.get('tags')
            hub_item_documentation_link = inner_hub_items_json.get('documentationLink')
            hub_item_marketing_link = inner_hub_items_json.get('marketingLink')
            hub_item_coming_soon = inner_hub_items_json.get('comingSoon')
            hub_item_artifact_id = inner_hub_items_json.get('artifactId')
            has_description_blocks = inner_hub_items_json.get('hasDescriptionBlocks')
            if show_description_blocks and has_description_blocks:
                hub_technology_description_list = get_technology_description_blocks(env, token, hub_item_id)
                print(f'{hub_item_type}|{hub_item_id}|{hub_item_name}|{hub_item_description}|{hub_item_tags}|{hub_item_documentation_link}|{hub_item_marketing_link}|{hub_item_coming_soon}|{hub_item_artifact_id}')
                for hub_technology_description in hub_technology_description_list:
                    print(hub_technology_description)
            else:
                print(f'{hub_item_type}|{hub_item_id}|{hub_item_name}|{hub_item_description}|{hub_item_tags}|{hub_item_documentation_link}|{hub_item_marketing_link}|{hub_item_coming_soon}|{hub_item_artifact_id}')


def get_technology_description_blocks(env, token, hub_technology_id):
    technology_description_blocks = []
    endpoint = f'/api/v2/hub/technologies/{hub_technology_id}' 
    params = ''
    hub_technology_json = get_rest_api_json(env, token, endpoint, params)[0]
    if not hub_technology_json.get('error'):
        hub_technology_description_blocks = hub_technology_json.get('descriptionBlocks')
        if hub_technology_description_blocks:
            for hub_technology_description_block in hub_technology_description_blocks:
                source = technology_description_blocks.append(hub_technology_description_block.get('source'))
                if source:
                    technology_description_blocks.append(source)
    return technology_description_blocks


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
    # process_hub_categories(env, token)
    process_hub_items(env, token, False)

if __name__ == '__main__':
    main()
