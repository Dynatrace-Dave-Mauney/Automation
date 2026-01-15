import json
import os
import re

from Reuse import environment
from Reuse import new_platform_api

# Populated from configuration file
owner_id_list = None


def process(env, env_name, client_id, client_secret):
    configuration_file = 'configurations.yaml'
    my_owner_ids = environment.get_configuration('my_owner_ids', configuration_file=configuration_file)

    if my_owner_ids:
        print('Downloading documents owned by:', my_owner_ids)

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
        if document_type == 'notebook':

            # filter by owner id, if needed
            document_owner = document.get('owner')
            if not my_owner_ids or (my_owner_ids and document_owner in my_owner_ids):
            # if my_owner_ids and document_owner in my_owner_ids:
                pass
            else:
                continue

            document_id = document.get('id')
            document_name = document.get('name')
            notebook_results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents/{document_id}/content', None)
            notebook_json = json.loads(notebook_results.text)
            notebook_metadata_results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents/{document_id}/metadata', None)
            notebook_metadata_json = json.loads(notebook_metadata_results.text)
            clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{document_name}.json')
            notebook_file_name = os.path.join(output_directory, clean_filename)
            formatted_notebook = json.dumps(notebook_json, indent=4, sort_keys=False)
            print(f'Writing file {notebook_file_name}')
            with open(notebook_file_name, 'w', encoding='utf8') as output_file:
                output_file.write('%s' % formatted_notebook)

            clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{document_name}.metadata.json')
            notebook_metadata_file_name = os.path.join(output_directory, clean_filename)
            formatted_notebook_metadata = json.dumps(notebook_metadata_json, indent=4, sort_keys=False)
            print(f'Writing file {notebook_metadata_file_name}')
            with open(notebook_metadata_file_name, 'w', encoding='utf8') as output_file:
                output_file.write('%s' % formatted_notebook_metadata)


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Personal'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, env_name, client_id, client_secret)


if __name__ == '__main__':
    main()
