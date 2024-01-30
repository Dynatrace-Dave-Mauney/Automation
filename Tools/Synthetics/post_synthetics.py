import json

from Reuse import dynatrace_api
from Reuse import environment


"""

POST HTTP_CHECK synthetics based on a template, changing the following fields per synthetic:

    Name
    Description
    URL
    HTTP Statuses
    Locations

"""
import copy

locations = {
    'Personal': ['GEOLOCATION-A'],
    'NonProd': ['SYNTHETIC_LOCATION-X'],
    'Prod': ['SYNTHETIC_LOCATION-Y', 'SYNTHETIC_LOCATION-Z']
    }


def process():
    # Test
    post_default_http_check(target_env_name='Personal', monitor_name='A', monitor_urls=['https://dynatrace.com'])


def post_default_http_check(target_env_name, monitor_name, monitor_urls):
    post_http_check(target_env_name, monitor_name, monitor_urls)


def load_http_check_template():
    with open('http_check_template.json', 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def post_http_check(target_env_name, monitor_name, monitor_urls):
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    endpoint = '/api/v1/synthetic/monitors'

    monitor = load_http_check_template()
    monitor['name'] = monitor_name
    monitor['locations'] = locations.get(target_env_name)
    monitor_http_statuses = '401, 403, 2xx, 3xx'
    monitor_request_template = monitor['script']['requests'][0]

    monitor_requests = []

    for monitor_url in monitor_urls:
        monitor_request = copy.deepcopy(monitor_request_template)
        monitor_request['description'] = str(monitor_url).replace('https://', '')
        monitor_request['url'] = monitor_url
        monitor_requests_validation_rules = monitor_request['validation']['rules'][0]
        monitor_requests_validation_rules['value'] = monitor_http_statuses
        monitor_requests.append(monitor_request)

    monitor['script']['requests'] = monitor_requests

    formatted_monitor = json.dumps(monitor, indent=4, sort_keys=False)
    # print(formatted_monitor)

    response = dynatrace_api.post_object(f'{env}{endpoint}', token, formatted_monitor)
    new_entity_id = json.loads(response.text).get('entityId')

    print(f'Posted {monitor_name} to {env_name} ({env}) with entity id {new_entity_id}')
    print('')


def main():
    process()


if __name__ == '__main__':
    main()
