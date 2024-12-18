import json
import os
import re

from Reuse import environment
from Reuse import new_platform_api


def process(env, env_name, client_id, client_secret):
    # The admin-access parameter results in a 403-Forbidden if the USER who created the client
    # does not have the "document:documents:admin" scope set
    # Tested it out only for the initial get documents call (so far) before deciding not to use it (yet)

    # scope = 'document:documents:admin document:documents:read'
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
    for document in document_list:
        document_type = document.get('type')
        if document_type == 'dashboard':
            document_id = document.get('id')
            document_name = document.get('name')
            # print(document_type, document_id, document_name)
            # dashboard_results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents/{document_id}/content', None)
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
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Sandbox'
    #
    # env_name_supplied = 'Upper'
    # env_name_supplied = 'Lower'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, env_name, client_id, client_secret)


if __name__ == '__main__':
    main()
