import json

from Reuse import environment
from Reuse import new_platform_api
from Reuse import report_writer


def process(env, client_id, client_secret, openpipeline_type):
    scope = 'openpipeline:configurations:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000, 'only-compatible': False}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/openpipeline/v1/configurations/{openpipeline_type}', params)
    openpipelines_json = json.loads(results.text)
    # print(openpipelines_json)

    pipelines = openpipelines_json.get('pipelines')
    routes = openpipelines_json.get('routing').get('entries')

    for pipeline in pipelines:
        # print(pipeline)
        print(pipeline.get('displayName'), pipeline.get('id'), pipeline.get('enabled'))

    for route in routes:
    #     print(route)
        print(route.get('note'), route.get('pipelineId'), route.get('enabled'))


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

    process(env, client_id, client_secret, 'logs')

    # Not very useful, and needs customization if used later
    # process(env, client_id, client_secret, 'categories')


if __name__ == '__main__':
    main()
