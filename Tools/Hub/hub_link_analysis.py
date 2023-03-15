#
# Compare links from Hub UI and API.
# Output is written to the console in pipe-delimited format, to an Excel spreadsheet and to an HTML page.
#

import requests
from bs4 import BeautifulSoup

from Reuse import dynatrace_api
from Reuse import environment


def get_links_from_api(env, token):
    result = {}

    endpoint = '/api/v2/hub/items'
    params = ''
    hub_items_json_list = dynatrace_api.get(env, token, endpoint, params)
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


def main():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    print('Hub Summary')

    api_links = get_links_from_api(env, token)
    ui_links = get_links_from_ui()
    # compare(api_links, ui_links)
    build_fall_back_links(api_links, ui_links)

if __name__ == '__main__':
    main()

