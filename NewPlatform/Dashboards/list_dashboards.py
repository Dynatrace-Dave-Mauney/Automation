import json

from Reuse import environment
from Reuse import new_platform_api
from Reuse import report_writer

selected_owners = [
    # '78cfc22b-0015-409e-bb07-0364eecc6ac3', # Me
    'ed29e85d-9e5f-4157-a2b8-563dc624708f', # Dynatrace
    '50436aec-8901-4282-ae81-690bd6509b18', # Dynatrace
]

def process(env, client_id, client_secret):
    scope = 'document:documents:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params)
    documents_json = json.loads(results.text)
    document_list = documents_json.get('documents')
    headers = [['Dashboard Name', 'Dashboard ID']]
    rows = []
    for document in document_list:
        # print(document)
        document_type = document.get('type')
        if document_type == 'dashboard':
            document_id = document.get('id')
            document_name = document.get('name')
            document_owner = document.get('owner')

            if document_owner in selected_owners:
                # rows.append([document_name, document_id])
                rows.append([document_name, document_id])

    report_writer.print_rows(headers, sorted(rows))

    for row in sorted(rows):
        print(f"\t\t'{row[0]}',")

def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Sandbox'
    env_name_supplied = 'PreProd'
    # env_name_supplied = 'Prod'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, client_id, client_secret)


if __name__ == '__main__':
    main()
