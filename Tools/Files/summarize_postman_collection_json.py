import os
import glob
import json


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


def main():
    selected_count = 0
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

    print(f'Total Selected: {selected_count}')


def process_item_list(item_list):
    for item in item_list:
        inner_item_list = item.get('item')

        if inner_item_list:
            inner_item_name = item.get('name')
            print('', 'BRANCH', inner_item_name)
            process_item_list(inner_item_list)
        else:
            inner_item_name = item.get('name')
            # print('', 'LEAF', inner_item_name)
            process_item(item)


def process_item(item):
    item_name = item.get('name')
    item_request = item.get('request')
    item_request_method = item_request.get('method')
    item_request_url = item_request.get('url', {'raw': ''})
    item_request_url_raw = replace_placeholders(item_request_url.get('raw'))
    item_request_body = item_request.get('body', {'raw': ''})
    item_request_body_raw = replace_placeholders(item_request_body.get('raw'))

    print(' ', 'LEAF', item_name, item_request_method, item_request_url_raw, item_request_body_raw)


def replace_placeholders(string):
    for variable in variables:
        string = string.replace('{{' + variable[0] + '}}', variable[1])

    return string


if __name__ == '__main__':
    main()
