import json

from Reuse import environment
from Reuse import new_platform_api
from Reuse import report_writer


def process(env, client_id, client_secret):
    scope = 'automation:workflows:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000, 'only-compatible': False}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/hub/v1/catalog/apps', params)
    workflows_json = json.loads(results.text)
    # print(workflows_json)
    workflow_list = workflows_json.get('results')
    headers = [['ID', 'Title', 'Description', 'Version']]
    rows = []
    for workflow in workflow_list:
        workflow_id = workflow.get('id')
        workflow_title = workflow.get('title')
        workflow_description = workflow.get('description')
        workflow_version = workflow.get('version')
        rows.append([workflow_id, workflow_title, workflow_description, workflow_version])

    report_writer.print_rows(headers, sorted(rows))


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
