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

    direct_share_dict = get_direct_share_dict(env, client_id, client_secret)
    document_id_list = get_document_id_list(env, client_id, client_secret)
    # print(direct_share_dict)
    # print(document_id_list)

    for document_id in document_id_list:
        already_shared_document_ids = direct_share_dict.keys()
        if document_id not in already_shared_document_ids:
            # print(f'{document_id} is not yet shared!')
            # direct_share_id = share_document(env, client_id, client_secret, document_id, 'read-write')
            results_text = share_document(env, client_id, client_secret, document_id, 'read-write')
            print(f'Shared: {results_text}')
        else:
            print(f'{document_id} is already shared')


def get_direct_share_dict(env, client_id, client_secret):
    direct_share_dict = {}
    scope = 'document:direct-shares:read'
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/direct-shares', params)
    direct_shares_json = json.loads(results.text)
    direct_share_list = direct_shares_json.get('direct-shares')

    next_page_key = direct_shares_json.get('nextPageKey')
    while next_page_key:
        oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
        params = {'page-size': 1000, 'page-key': next_page_key}
        results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params=params)
        direct_shares_json = json.loads(results.text)
        direct_share_list.extend(direct_shares_json.get('documents'))
        next_page_key = direct_shares_json.get('nextPageKey')

    for direct_share in direct_share_list:
        direct_share_id = direct_share.get('id')
        direct_share_document_id = direct_share.get('documentId')
        direct_share_dict[direct_share_document_id] = direct_share_id

    return direct_share_dict


def get_document_id_list(env, client_id, client_secret):
    document_id_list = []
    scope = 'document:documents:read'
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params)
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

    for document in document_list:
        # print(document)
        document_id = document.get('id')
        document_name = document.get('name')
        document_owner = document.get('owner')
        # print(document_name, document_owner)

        if document_owner not in owner_id_list:
            # print(f'Skipping document with owner not in the configured owner list: {document_owner}')
            continue

        # Only share "official" dashboards with environment prefixes
        # if document_name.startswith('Prod ') or document_name.startswith('NonProd ') or document_name.startswith('Int '):
        if document_name.startswith('['):
            print(f'{document_name} will be shared')
            document_id_list.append(document_id)

    return document_id_list


def share_document(env, client_id, client_secret, document_id, access):
    scope = 'document:direct-shares:write'
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    payload = json.dumps({'documentId': document_id, 'access': access,
                          "recipients": [
                              {
                                  "id": "041fdd66-0e7f-4272-9c69-33a00cf84fb0",
                                  "type": "group"
                              }]})
    results = new_platform_api.post(oauth_bearer_token, f'{env}/platform/document/v1/direct-shares?send-notification=false&admin-access=false', payload)
    return results.text


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    env_name_supplied = 'NonProd'
    # env_name_supplied = 'Int'
    # env_name_supplied = 'Personal'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, client_id, client_secret)


if __name__ == '__main__':
    main()
