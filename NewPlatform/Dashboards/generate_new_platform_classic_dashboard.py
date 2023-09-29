import json

from Reuse import environment
from Reuse import new_platform_api


def process(env, client_id, client_secret):
    document_id_dict = get_document_id_dict(env, client_id, client_secret)
    # print(f'document_id_dict: {document_id_dict}')

    scope = 'document:environment-shares:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/environment-shares', params)
    environment_shares_json = json.loads(results.text)
    environment_share_list = environment_shares_json.get('environment-shares')
    # print(f'environment_share_list: {environment_share_list}')

    dashboard_markdown_list = []
    notebook_markdown_list = []

    for environment_share in environment_share_list:
        environment_share_id = environment_share.get('id')
        environment_share_document_id = environment_share.get('documentId')
        document_id_dict_values = document_id_dict[environment_share_document_id]
        if not document_id_dict_values:
            print('Document ID not found.  Aborting.')
            exit(1)
        document_name = document_id_dict_values.get('name')
        document_type = document_id_dict_values.get('type')
        markdown = f'[{document_name}]({env}/ui/document/v0/#share={environment_share_id})'
        if document_type == 'dashboard':
            dashboard_markdown_list.append(markdown)
        else:
            if document_type == 'notebook':
                notebook_markdown_list.append(markdown)
            else:
                print(f'Unexpected document type: {document_type}')

    # print(sorted(dashboard_markdown_list))
    # print(sorted(notebook_markdown_list))

    generate_new_platform_classic_dashboard(env, sorted(dashboard_markdown_list), sorted(notebook_markdown_list))


def get_document_id_dict(env, client_id, client_secret):
    document_id_dict = {}
    scope = 'document:documents:read'
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params)
    documents_json = json.loads(results.text)
    document_list = documents_json.get('documents')
    for document in document_list:
        document_id = document.get('id')
        document_name = document.get('name')
        document_type = document.get('type')
        document_id_dict[document_id] = {'name': document_name, 'type': document_type}

    return document_id_dict


def generate_new_platform_classic_dashboard(env, dashboard_markdown_list, notebook_markdown_list):
    EOL = '\n\n'
    SEP = '---\n\n'
    dashboard_json = load_dashboard_template()
    dashboard_tiles = dashboard_json.get('tiles')
    # print(dashboard_tiles)
    generated_markdown = '## Custom Dashboards'
    generated_markdown += EOL
    for dashboard_markdown in dashboard_markdown_list:
        generated_markdown += dashboard_markdown
        generated_markdown += EOL

    generated_markdown += SEP
    generated_markdown += '## Custom Notebooks'
    generated_markdown += EOL
    for notebook_markdown in notebook_markdown_list:
        generated_markdown += notebook_markdown
        generated_markdown += EOL

    generated_markdown += SEP
    generated_markdown += '## Views'
    generated_markdown += EOL

    generated_markdown += f'[Dashboards]({env}/ui/apps/dynatrace.dashboards)'
    generated_markdown += EOL
    generated_markdown += f'[Notebooks]({env}/ui/apps/dynatrace.notebooks)'
    generated_markdown += EOL
    generated_markdown += f'[Workflows]({env}/ui/apps/dynatrace.automations)'
    generated_markdown += EOL
    generated_markdown += f'[Hub]({env}/ui/apps/dynatrace.hub)'
    generated_markdown += EOL
    generated_markdown += f'[API]({env}/platform/swagger-ui/index.html)'
    generated_markdown += EOL

    """
    ## Views\n\n
    [Dashboards](https://pey66649.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboards)\n\n
    [Notebooks](https://pey66649.apps.dynatrace.com/ui/apps/dynatrace.notebooks/)\n\n
    [Workflows](https://pey66649.apps.dynatrace.com/ui/apps/dynatrace.automations/)\n\n
    [Hub](https://pey66649.apps.dynatrace.com/ui/apps/dynatrace.hub)\n\n
    [API](https://pey66649.apps.dynatrace.com/platform/swagger-ui/index.html)\n"
    """

    dashboard_tiles[0]['markdown'] = generated_markdown
    write_dashboard(dashboard_json)


def load_dashboard_template():
    with open('new_platform_dashboard_template.json', 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def write_dashboard(dashboard_json):
    with open('new_platform_dashboard.json', 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(dashboard_json, indent=4, sort_keys=False))


def main():
    friendly_function_name = 'Dynatrace Platform Document'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, client_id, client_secret)


if __name__ == '__main__':
    main()
