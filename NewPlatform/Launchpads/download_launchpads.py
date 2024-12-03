import json
import os
import re

from Reuse import environment
from Reuse import new_platform_api


def process(env, env_name, client_id, client_secret):
    scope = 'document:documents:read'

    output_directory = environment.get_output_directory_name(f"Downloads/{env_name}")
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params=params)
    documents_json = json.loads(results.text)
    document_list = documents_json.get('documents')
    for document in document_list:
        document_type = document.get('type')
        if document_type == 'launchpad':
            document_id = document.get('id')
            document_name = document.get('name')
            launchpad_results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents/{document_id}/content', None)
            launchpad_json = json.loads(launchpad_results.text)
            launchpad_metadata_results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents/{document_id}/metadata', None)
            launchpad_metadata_json = json.loads(launchpad_metadata_results.text)
            clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{document_name}.json')
            launchpad_file_name = os.path.join(output_directory, clean_filename)
            formatted_launchpad = json.dumps(launchpad_json, indent=4, sort_keys=False)
            print(f'Writing file {launchpad_file_name}')
            with open(launchpad_file_name, 'w', encoding='utf8') as output_file:
                output_file.write('%s' % formatted_launchpad)

            clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{document_name}.metadata.json')
            launchpad_metadata_file_name = os.path.join(output_directory, clean_filename)
            formatted_launchpad_metadata = json.dumps(launchpad_metadata_json, indent=4, sort_keys=False)
            print(f'Writing file {launchpad_metadata_file_name}')
            with open(launchpad_metadata_file_name, 'w', encoding='utf8') as output_file:
                output_file.write('%s' % formatted_launchpad_metadata)


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Sanbox'
    #
    # env_name_supplied = 'Upper'
    # env_name_supplied = 'Lower'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, env_name, client_id, client_secret)


if __name__ == '__main__':
    main()
