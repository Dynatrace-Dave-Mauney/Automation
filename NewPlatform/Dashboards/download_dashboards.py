import json
import os
import re

from Reuse import environment
from Reuse import new_platform_api

# Populated from configuration file
my_owner_ids = None


def process(env, env_name, client_id, client_secret):
    configuration_file = 'configurations.yaml'

    my_owner_ids = environment.get_configuration('my_owner_ids', configuration_file=configuration_file)

    # To get all...
    my_owner_ids = None

    if my_owner_ids:
        print('Downloading documents owned by:', my_owner_ids)

    scope = 'document:documents:read'

    output_directory = environment.get_output_directory_name(f"Downloads/{env_name}")
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    # params = {'page-size': 1000, 'admin-access': True}
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params=params)
    documents_json = json.loads(results.text)
    document_list = documents_json.get('documents')

    next_page_key = documents_json.get('nextPageKey')
    while next_page_key:
        oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
        params = {'page-size': 1000, 'page-key': next_page_key}
        results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params=params)
        documents_json = json.loads(results.text)
        document_list.extend(documents_json.get('documents'))
        next_page_key = documents_json.get('nextPageKey')

    # print('Documents:', len(document_list))
    #
    # alpha_list = []
    # for document in document_list:
    #     document_name = document.get('name')
    #     if '[splunk]' in document_name.lower():
    #         if document_name not in alpha_list:
    #             alpha_list.append(document_name)
    #
    # print('Splunk Documents:', len(alpha_list))
    # for document_name in sorted(alpha_list):
    #     print(document_name)
    #
    # if len(alpha_list) > 0:
    #     exit(9999)

    for document in document_list:
        document_type = document.get('type')
        if document_type == 'dashboard':

            # filter by owner id, if needed
            document_owner = document.get('owner')
            if not my_owner_ids or (my_owner_ids and document_owner in my_owner_ids):
                pass
            else:
                continue

            document_id = document.get('id')
            document_name = document.get('name')

            # if not document_name.startswith('TEMPLATE - '):
            if '[Splunk]' not in document_name:
                print(f'Skipping {document_name}')
                continue

            # print(document_type, document_id, document_name)
            # dashboard_results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents/{document_id}/content', None)
            oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
            dashboard_results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents/{document_id}/content', None)
            dashboard_json = json.loads(dashboard_results.text)
            dashboard_metadata_results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents/{document_id}/metadata', None)
            dashboard_metadata_json = json.loads(dashboard_metadata_results.text)
            # print(dashboard_metadata_json)
            clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{document_name}.json')
            dashboard_file_name = os.path.join(output_directory, clean_filename)
            formatted_dashboard = json.dumps(dashboard_json, indent=4, sort_keys=False)
            print(f'Writing file {dashboard_file_name}')
            with open(dashboard_file_name, 'w', encoding='utf8') as output_file:
                output_file.write('%s' % formatted_dashboard)

            clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{document_name}.metadata.json')
            dashboard_metadata_file_name = os.path.join(output_directory, clean_filename)
            formatted_dashboard_metadata = json.dumps(dashboard_metadata_json, indent=4, sort_keys=False)
            print(f'Writing file {dashboard_metadata_file_name}')
            with open(dashboard_metadata_file_name, 'w', encoding='utf8') as output_file:
                output_file.write('%s' % formatted_dashboard_metadata)


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    env_name_supplied = 'NonProd'
    # env_name_supplied = 'Int'
    # env_name_supplied = 'Personal'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, env_name, client_id, client_secret)


if __name__ == '__main__':
    main()
