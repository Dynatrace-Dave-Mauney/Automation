import json

from Reuse import environment
from Reuse import new_platform_api
from Reuse import report_writer


def process(env, client_id, client_secret, hub_type):
    scope = 'hub:catalog:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000, 'only-compatible': False}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/hub/v1/catalog/{hub_type}', params)
    hub_apps_json = json.loads(results.text)
    # print(hub_apps_json)

    if hub_type == 'categories':
        hub_app_list = hub_apps_json.get('categories')
    else:
        hub_app_list = hub_apps_json.get('items')

    headers = [['ID', 'Title', 'Description', 'Version']]
    rows = []
    for hub_app in hub_app_list:
        hub_app_id = hub_app.get('id')
        hub_app_type = hub_app.get('type')
        hub_app_version = hub_app.get('version')
        hub_app_name = hub_app.get('name')
        hub_app_description = hub_app.get('description')
        rows.append([hub_app_id, hub_app_type, hub_app_name, hub_app_version, hub_app_description])

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

    process(env, client_id, client_secret, 'apps')
    process(env, client_id, client_secret, 'extensions')
    process(env, client_id, client_secret, 'technologies')

    # Not very useful, and needs customization if used later
    # process(env, client_id, client_secret, 'categories')


if __name__ == '__main__':
    main()
