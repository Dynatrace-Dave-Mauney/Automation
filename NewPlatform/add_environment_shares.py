import json

from Reuse import environment
from Reuse import new_platform_api

# Populated from configuration file
owner_id_list = None

def process(env, client_id, client_secret):
    configuration_file = 'configurations.yaml'
    owner_ids = environment.get_configuration('my_owner_ids', configuration_file=configuration_file)

    print('Sharing documents owned by:', owner_ids)
    global owner_id_list
    owner_id_list = owner_ids

    environment_share_dict = get_environment_share_dict(env, client_id, client_secret)
    document_id_list = get_document_id_list(env, client_id, client_secret)
    # print(environment_share_dict)
    # print(document_id_list)

    for document_id in document_id_list:
        already_shared_document_ids = environment_share_dict.keys()
        if document_id not in already_shared_document_ids:
            # print(f'{document_id} is not yet shared!')
            # environment_share_id = share_document(env, client_id, client_secret, document_id, 'read-write')
            results_text = share_document(env, client_id, client_secret, document_id, 'read')
            print(f'Shared: {results_text}')


def get_environment_share_dict(env, client_id, client_secret):
    environment_share_dict = {}
    scope = 'document:environment-shares:read'
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/environment-shares', params)
    environment_shares_json = json.loads(results.text)
    environment_share_list = environment_shares_json.get('environment-shares')
    for environment_share in environment_share_list:
        environment_share_id = environment_share.get('id')
        environment_share_document_id = environment_share.get('documentId')
        environment_share_dict[environment_share_document_id] = environment_share_id

    return environment_share_dict


def get_document_id_list(env, client_id, client_secret):
    document_id_list = []
    scope = 'document:documents:read'
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params)
    documents_json = json.loads(results.text)
    document_list = documents_json.get('documents')
    for document in document_list:
        # print(document)
        document_id = document.get('id')
        document_name = document.get('name')
        document_owner = document.get('owner')
        print(document_owner)

        if document_owner in owner_id_list:
            # pass
            print('Skipping document with owner not in the configured owner list')
        else:
            continue

        # Skip Events dashboards/notebooks since queries have a cost
        if 'Events' not in document_name:
            document_id_list.append(document_id)

    return document_id_list


def share_document(env, client_id, client_secret, document_id, access):
    scope = 'document:environment-shares:write'
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    payload = json.dumps({'documentId': document_id, 'access': access})
    results = new_platform_api.post(oauth_bearer_token, f'{env}/platform/document/v1/environment-shares', payload)
    return results.text


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
    process(env, client_id, client_secret)


if __name__ == '__main__':
    main()
