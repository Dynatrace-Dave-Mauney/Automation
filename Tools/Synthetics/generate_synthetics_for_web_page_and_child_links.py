import copy
import json
import requests

from bs4 import BeautifulSoup

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token, root_page):
    page = requests.get(root_page)
    soup = BeautifulSoup(page.text, 'html.parser')

    child_url_list = []
    for link in soup.find_all('a'):
        href = link.get('href')

        # For each relative URL, create an absolute URL and add to the list
        if href.startswith('/'):
            child_url_list.append(root_page + href)

    unique_child_urls = remove_duplicates(sorted(child_url_list))

    # post_http_check_synthetic(env, token, root_page, unique_child_urls)
    post_browser_synthetic(env, token, root_page, unique_child_urls)


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


def post_http_check_synthetic(env, token, root_page, child_pages):
    file_path = f'standard_http_check_template_GET.json'
    f = open(file_path)
    data = json.load(f)

    name = f'Check Root and Children for {root_page}'
    data['name'] = name
    data['locations'] = ['GEOLOCATION-9999453BE4BDB3CD']
    '''N. Virginia: GEOLOCATION-9999453BE4BDB3CD'''
    '''Ohio: GEOLOCATION-716844F67F8B2CA0'''
    data['tags'] = [{"source": "USER", "context": "CONTEXTLESS", "key": "RobotAdmin"}]

    monitor_request_template = data['script']['requests'][0]

    # First, add the root page to the list
    monitor_request = build_http_check_request(monitor_request_template, root_page)
    monitor_request_list = [monitor_request]

    # Then, add the child pages to the list
    for child_page in child_pages:
        monitor_request = build_http_check_request(monitor_request_template, child_page)
        monitor_request_list.append(monitor_request)

    data['script']['requests'] = monitor_request_list

    formatted_json = json.dumps(data, indent=4, sort_keys=False)
    print(formatted_json)

    endpoint = '/api/v1/synthetic/monitors'
    print(f'Posting HTTP Check Synthetic "{name}" to {env}{endpoint}')
    r = dynatrace_api.post_object(f'{env}{endpoint}', token, formatted_json)
    print(f'HTTP Check Synthetic Response: {r.text}')
    monitor_id = json.loads(r.text).get('entityId')
    print(f'Verify: {env}/ui/http-monitor/{monitor_id}')


def build_http_check_request(monitor_request_template, url):
    monitor_request = copy.deepcopy(monitor_request_template)
    monitor_request['url'] = url
    url_short_name = url.lower().strip().replace('https://', '')
    monitor_request['description'] = f'{url_short_name}'
    monitor_requests_validation_rules = monitor_request['validation']['rules'][0]
    monitor_requests_validation_rules['value'] = '200'
    return monitor_request


def post_browser_synthetic(env, token, root_page, child_pages):
    file_path = f'standard_browser_template.json'
    f = open(file_path)
    data = json.load(f)

    name = f'Browser Check Root and Children for {root_page}'
    data['name'] = name
    data['locations'] = ['GEOLOCATION-9999453BE4BDB3CD']
    data['tags'] = [{"source": "USER", "context": "CONTEXTLESS", "key": "RobotAdmin"}]

    monitor_event_template = data['script']['events'][0]

    # First, add the root page to the list
    monitor_event = build_browser_event(monitor_event_template, root_page)
    monitor_event_list = [monitor_event]

    # Then, add the child pages to the list
    for child_page in child_pages:
        monitor_event = build_browser_event(monitor_event_template, child_page)
        monitor_event_list.append(monitor_event)

    # Use "clickpath" to allow for multiple events (availability allows only a single URL
    data['script']['type'] = 'clickpath'
    data['script']['events'] = monitor_event_list

    formatted_json = json.dumps(data, indent=4, sort_keys=False)
    print(formatted_json)

    endpoint = '/api/v1/synthetic/monitors'
    print(f'Posting Browser Synthetic "{name}" to {env}{endpoint}')
    r = dynatrace_api.post_object(f'{env}{endpoint}', token, formatted_json)
    print(f'HTTP Check Synthetic Response: {r.text}')
    monitor_id = json.loads(r.text).get('entityId')
    print(f'Verify: {env}/ui/http-monitor/{monitor_id}')


def build_browser_event(monitor_event_template, url):
    monitor_event = copy.deepcopy(monitor_event_template)
    monitor_event['url'] = url
    url_short_name = url.lower().strip().replace('https://', '')
    monitor_event['description'] = f'{url_short_name}'
    return monitor_event


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    env_name_supplied = 'Personal'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    configuration_file = 'configurations.yaml'
    root_page = environment.get_configuration('root_page', configuration_file=configuration_file)
    if not root_page:
        print(f'A value for "root_page" must be provided in {configuration_file}')
        exit(1)

    process(env, token, root_page)


if __name__ == '__main__':
    main()
