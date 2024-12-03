import json

from Reuse import environment
from Reuse import new_platform_api

# Use configurations.yaml to set this variable
my_owner_ids = []

shared_dashboard_template = {
    "version": 1,
    "variables": [],
    "tiles": {
        "0": {
            "type": "markdown",
            "title": "",
            "content": ""
        }
    },
    "layouts": {
        "0": {
            "x": 0,
            "y": 0,
            "w": 24,
            "h": 13
        }
    },
    "importedWithCode": False
}

shared_notebook_template = {
    "version": "1",
    "defaultTimeframe": {
        "from": "now()-2h",
        "to": "now()"
    },
    "sections": [
        {
            "id": "aaaaaaaa-bbbb-cccc-dddd-000000000001",
            "type": "markdown",
            "markdown": ""
        }
    ]
}


def process(env, client_id, client_secret):
    configuration_file = 'configurations.yaml'
    global my_owner_ids
    my_owner_ids = environment.get_configuration('my_owner_ids', configuration_file=configuration_file)

    environment_shares = get_environment_shares(env, client_id, client_secret)
    dashboards = get_dashboards(env, client_id, client_secret)
    notebooks = get_notebooks(env, client_id, client_secret)
    generate_dashboard(env, environment_shares, dashboards)
    generate_notebook(env, environment_shares, notebooks)


def generate_dashboard(env, environment_shares, dashboards):
    shared_dashboard = shared_dashboard_template
    shared_markdown_string = ''

    links = []
    dashboard_ids = dashboards.keys()
    for dashboard_id in dashboard_ids:
        environment_shares.get(dashboard_id)
        environment_share_id = environment_shares.get(dashboard_id)
        if environment_share_id:
            dashboard_name = dashboards.get(dashboard_id)
            links.append(f'[{dashboard_name}]({env}/ui/dashboard/v0/#share={environment_share_id})  \n')

    for link in sorted(links):
        shared_markdown_string += link

    shared_dashboard["tiles"]["0"]["content"] = shared_markdown_string

    # print(shared_dashboard)
    write_dashboard(shared_dashboard)


def generate_notebook(env, environment_shares, notebooks):
    shared_notebook = shared_notebook_template
    shared_markdown_string = ''

    links = []
    notebook_ids = notebooks.keys()
    for notebook_id in notebook_ids:
        environment_shares.get(notebook_id)
        environment_share_id = environment_shares.get(notebook_id)
        if environment_share_id:
            notebook_name = notebooks.get(notebook_id)
            links.append(f'[{notebook_name}]({env}/ui/notebook/v0/#share={environment_share_id})  \n')

    for link in sorted(links):
        shared_markdown_string += link

    shared_notebook["sections"][0]["markdown"] = shared_markdown_string

    # print(shared_notebook)
    write_notebook(shared_notebook)


def get_environment_shares(env, client_id, client_secret):
    environment_shares = {}

    scope = 'document:environment-shares:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/environment-shares', params)
    environment_shares_json = json.loads(results.text)
    environment_share_list = environment_shares_json.get('environment-shares')
    for environment_share in environment_share_list:
        environment_share_id = environment_share.get('id')
        environment_share_document_id = environment_share.get('documentId')
        # environment_shares[environment_share_id] = environment_share_document_id
        environment_shares[environment_share_document_id] = environment_share_id

    return environment_shares


def get_dashboards(env, client_id, client_secret):
    dashboards = {}

    scope = 'document:documents:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params)
    dashboards_json = json.loads(results.text)
    dashboard_list = dashboards_json.get('documents')
    for dashboard in dashboard_list:
        dashboard_type = dashboard.get('type')
        if dashboard_type == 'dashboard':
            dashboard_id = dashboard.get('id')
            dashboard_name = dashboard.get('name')
            dashboard_owner = dashboard.get('owner')

            if dashboard_owner in my_owner_ids:
                dashboards[dashboard_id] = dashboard_name

    return dashboards


def get_notebooks(env, client_id, client_secret):
    notebooks = {}

    scope = 'document:documents:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params)
    notebooks_json = json.loads(results.text)
    notebook_list = notebooks_json.get('documents')
    for notebook in notebook_list:
        notebook_type = notebook.get('type')
        if notebook_type == 'notebook':
            notebook_id = notebook.get('id')
            notebook_name = notebook.get('name')
            notebook_owner = notebook.get('owner')

            if notebook_owner in my_owner_ids:
                notebooks[notebook_id] = notebook_name

    return notebooks


def write_dashboard(dashboard_json):
    with open('Shared Dashboards.json', 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(dashboard_json, indent=4, sort_keys=False))


def write_notebook(notebook_json):
    with open('Shared Notebooks.json', 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(notebook_json, indent=4, sort_keys=False))


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
