import json
import os
import re

from Reuse import environment
from Reuse import new_platform_api


def process(env, env_name, client_id, client_secret):
    scope = 'storage:bucket-definitions:read'

    output_directory = environment.get_output_directory_name(f"Downloads/{env_name}")
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/storage/management/v1/bucket-definitions', params=params)
    buckets_json = json.loads(results.text)
    # print(buckets_json)
    formatted_pipeline = json.dumps(buckets_json, indent=4, sort_keys=False)
    filename = f'{output_directory}/buckets.json'
    print(f'Writing file {filename}')
    with open(filename, 'w', encoding='utf8') as output_file:
        output_file.write('%s' % formatted_pipeline)


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, env_name, client_id, client_secret)


if __name__ == '__main__':
    main()
