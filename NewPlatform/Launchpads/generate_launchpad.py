# This module is likely obsolete

import copy
import json

from Reuse import environment
from Reuse import new_platform_api

# Use configurations.yaml to set this variable
my_owner_ids = []

launchpad_template = {
    "schemaVersion": 2,
    "icon": "default",
    "background": "default",
    "containerList": {
        "containers": [
            {
                "blocks": [],
                "horizontalLayoutWeight": 1
            }
        ]
    }
}

launchpad_block_template = {
    "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "type": "markdown",
    "properties": {
        "expanded": True
    },
    "content": ""
}


def process(env, client_id, client_secret):
    configuration_file = 'configurations.yaml'
    global my_owner_ids
    my_owner_ids = environment.get_configuration('my_owner_ids', configuration_file=configuration_file)

    environment_shares = get_environment_shares(env, client_id, client_secret)
    dashboards = get_dashboards(env, client_id, client_secret)
    notebooks = get_notebooks(env, client_id, client_secret)

    shared_launchpad = launchpad_template
    shared_launchpad_dashboard_block = generate_dashboard_block(env, environment_shares, dashboards)
    shared_launchpad_notebook_block = generate_notebook_block(env, environment_shares, notebooks)
    shared_launchpad_classic_dashboard_block = generate_classic_dashboard_block(env)
    shared_launchpad_launchpad_block = generate_launchpad_block(env)
    shared_university_block = generate_university_block()
    shared_documentation_block = generate_documentation_block()

    shared_launchpad_blocks = shared_launchpad['containerList']['containers'][0]['blocks']
    shared_launchpad_blocks.append(shared_launchpad_dashboard_block)
    shared_launchpad_blocks.append(shared_launchpad_notebook_block)
    shared_launchpad_blocks.append(shared_launchpad_launchpad_block)
    shared_launchpad_blocks.append(shared_launchpad_classic_dashboard_block)
    shared_launchpad_blocks.append(shared_university_block)
    shared_launchpad_blocks.append(shared_documentation_block)

    write_launchpad(shared_launchpad)


def generate_dashboard_block(env, environment_shares, dashboards):
    launchpad_block = copy.deepcopy(launchpad_block_template)
    shared_markdown_string = '#  Shared Dashboards  \n'

    links = []
    dashboard_ids = dashboards.keys()
    for dashboard_id in dashboard_ids:
        environment_shares.get(dashboard_id)
        environment_share_id = environment_shares.get(dashboard_id)
        if environment_share_id:
            dashboard_name = dashboards.get(dashboard_id)
            links.append(f'[{dashboard_name}]({env}/ui/document/v0/#share={environment_share_id})  \n')

    for link in sorted(links):
        shared_markdown_string += link

    launchpad_block['content'] = shared_markdown_string
    return launchpad_block


def generate_notebook_block(env, environment_shares, notebooks):
    launchpad_block = copy.deepcopy(launchpad_block_template)
    shared_markdown_string = '#  Shared Notebooks  \n'

    links = []
    notebook_ids = notebooks.keys()
    for notebook_id in notebook_ids:
        environment_shares.get(notebook_id)
        environment_share_id = environment_shares.get(notebook_id)
        if environment_share_id:
            notebook_name = notebooks.get(notebook_id)
            links.append(f'[{notebook_name}]({env}/ui/document/v0/#share={environment_share_id})  \n')

    for link in sorted(links):
        shared_markdown_string += link

    launchpad_block['content'] = shared_markdown_string
    return launchpad_block


def generate_classic_dashboard_block(env):
    launchpad_block = copy.deepcopy(launchpad_block_template)
    shared_markdown_string = '#  Classic Dashboards  \n'

    classic_tenant = env.replace('.apps.', '.live.')
    overview_dashboard_link = f'{classic_tenant}/#dashboard;id=00000000-dddd-bbbb-ffff-000000000001'
    shared_markdown_string += f'[Overview Dashboard]({overview_dashboard_link})'

    launchpad_block['content'] = shared_markdown_string
    return launchpad_block


def generate_launchpad_block(env):
    launchpad_block = copy.deepcopy(launchpad_block_template)
    shared_markdown_string = '#  Launchpads  \n'

    getting_started_launchpad_link = f'{env}/ui/apps/dynatrace.launcher/getting-started'
    shared_markdown_string += f'[Getting started with Dynatrace]({getting_started_launchpad_link})  \n'

    links = [
        '[What is Dynatrace and how to get started?](https://wkf10640.apps.dynatrace.com/ui/apps/dynatrace.launcher/launchpad/45d83fd1-675c-4f1c-82f4-58ab86a293f1)',
        '[Welcome to the Dynatrace Playground](https://wkf10640.apps.dynatrace.com/ui/apps/dynatrace.launcher/launchpad/99583c94-6c7c-4a5d-9c23-1432e4e1746c),'
    ]

    for link in links:
        shared_markdown_string += link + '  \n'

    launchpad_block['content'] = shared_markdown_string
    return launchpad_block


def generate_university_block():
    university_block = copy.deepcopy(launchpad_block_template)
    shared_markdown_string = '#  Dynatrace University  \n'

    links = [
        '[Beginner Level](https://university.dynatrace.com/ondemand?content=dynatrace&skillLevel=beginner)',
        '[Intermediate Level](https://university.dynatrace.com/ondemand?content=dynatrace&skillLevel=intermediate)',
        '[Advanced Level](https://university.dynatrace.com/ondemand?content=dynatrace&skillLevel=advanced)',
    ]

    for link in links:
        shared_markdown_string += link + '  \n'

    university_block['content'] = shared_markdown_string
    return university_block


def generate_documentation_block():
    documentation_block = copy.deepcopy(launchpad_block_template)
    shared_markdown_string = '#  Dynatrace Documentation  \n'

    links = [
        '[Dashboards and Notebooks](https://docs.dynatrace.com/docs/shortlink/dashboards-and-notebooks)',
        '[Distributed Tracing](https://docs.dynatrace.com/docs/shortlink/distributed-traces-grail)',
        '[DQL](https://docs.dynatrace.com/docs/shortlink/dql-dynatrace-query-language-hub)',
        '[Log Content Analysis](https://docs.dynatrace.com/docs/shortlink/lma-analysis)',
        '[Metrics](https://docs.dynatrace.com/docs/shortlink/metrics-grail)',
    ]

    for link in links:
        shared_markdown_string += link + '  \n'

    documentation_block['content'] = shared_markdown_string
    return documentation_block


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


def write_launchpad(launchpad_json):
    with open('Shared Launchpad.json', 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(launchpad_json, indent=4, sort_keys=False))


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
