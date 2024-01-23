import copy
import glob
import json
import os

from Reuse import dynatrace_api
from Reuse import environment

request_count = 0

variables = [
    ('account_number', '1'),
    ('apikey', '12'),
    ('claim_pro', '123'),
    ('csp_acct_number', '1234'),
    ('customer_service_root', '12345'),
    ('delivery_date', '123456'),
    ('document_pro', '1234567'),
    ('invoice_pro', '12345678'),
    ('password', 'password123'),
    ('pickup_date', '123456789'),
    ('pickup_number', '1234567890'),
    ('root', 'https://localhost'),
    ('soap_root', 'https://localhost'),
    ('soap_tracking_pro', '12345678901'),
    ('tracking_pro', '123456789012'),
    ('username', 'nobody'),
]


def post_http_check_synthetic(env, token, name, url, method, body, header_list):
    file_path = f'standard_http_check_template_{method}.json'
    f = open(file_path)
    data = json.load(f)

    locations = ['GEOLOCATION-9999453BE4BDB3CD']

    data['locations'] = locations
    # monitor_http_statuses = '2xx, 3xx, 401, 403'
    monitor_http_statuses = '2xx'
    monitor_request_template = data['script']['requests'][0]
    # monitor_requests = []

    new_header_list = []
    if header_list:
        for header in header_list:
            new_header = {}
            new_header['name'] = header.get('key')
            new_header['value'] = header.get('value')
            new_header_list.append(new_header)
            print('NEW HEADERS:', new_header_list)

    monitor_request = copy.deepcopy(monitor_request_template)
    data['name'] = name
    monitor_request['url'] = url.strip()
    url_short_name = url.lower().strip().replace('https://', '')
    monitor_request['description'] = f'{name}:{url_short_name}'
    monitor_request['method'] = method
    monitor_requests_validation_rules = monitor_request['validation']['rules'][0]
    monitor_requests_validation_rules['value'] = monitor_http_statuses
    monitor_configuration = monitor_request['configuration']
    monitor_configuration['requestHeaders'] = new_header_list
    monitor_request['configuration'] = monitor_configuration
    monitor_requests = [monitor_request]
    data['script']['requests'] = monitor_requests

    formatted_json = json.dumps(data, indent=4, sort_keys=False)
    print(formatted_json)

    endpoint = '/api/v1/synthetic/monitors'
    print(f'Posting HTTP Check Synthetic "{name}" to {env}{endpoint}')
    r = dynatrace_api.post_object(f'{env}{endpoint}', token, formatted_json)
    print(f'HTTP Check Synthetic Response: {r.text}')
    monitor_id = json.loads(r.text).get('entityId')
    print(f'Verify: {env}/ui/http-monitor/{monitor_id}')
    exit(1111)


def process_item_list(item_list):
    for item in item_list:
        inner_item_list = item.get('item')

        if inner_item_list:
            inner_item_name = item.get('name')
            print('', 'BRANCH', inner_item_name)
            process_item_list(inner_item_list)
        else:
            # inner_item_name = item.get('name')
            # print('', 'LEAF', inner_item_name)
            process_item(item)


def process_item(item):
    global request_count

    item_name = item.get('name')
    item_request = item.get('request')
    item_request_method = item_request.get('method')
    item_request_url = item_request.get('url', {'raw': ''})
    item_request_url_raw = replace_placeholders(item_request_url.get('raw'))
    item_request_body = item_request.get('body', {'raw': ''})
    item_request_body_raw = replace_placeholders(item_request_body.get('raw'))
    header_list = item_request.get('header')

    if header_list:
        print('HEADER:', header_list)

    print(' ', 'LEAF', item_name, item_request_method, item_request_url_raw, header_list, item_request_body_raw)

    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    env_name_supplied = 'Personal'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    post_http_check_synthetic(env, token, item_name, item_request_url_raw, item_request_method, item_request_body_raw, header_list)

    request_count += 1


def replace_placeholders(string):
    for variable in variables:
        string = string.replace('{{' + variable[0] + '}}', variable[1])

    return string


def main():
    try:
        input_glob_pattern = "C:\\Dynatrace\\Customers\\ODFL\\Synthetics\\IPL Web & API Tests.postman_collection.json"

        for file_name in glob.glob(input_glob_pattern, recursive=True):
            base_file_name = os.path.basename(file_name)
            print(base_file_name)
            if os.path.isfile(file_name) and file_name.endswith('.json'):
                with open(file_name, 'r', encoding='utf-8') as infile:
                    input_json = json.loads(infile.read())
                    # formatted_json = json.dumps(input_json, indent=4, sort_keys=False)
                    info = input_json.get('info')
                    collection_name = info.get('name')
                    print(collection_name)
                    item_list = input_json.get('item')
                    process_item_list(item_list)
    except FileNotFoundError:
        print('The directory name does not exist')

    print(f'Total Requests: {request_count}')


if __name__ == '__main__':
    main()
