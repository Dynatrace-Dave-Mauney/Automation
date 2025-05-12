import json

from Reuse import environment
from Reuse import new_platform_api


def process(env, client_id, client_secret):
    scope = 'storage:bucket-definitions:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000, 'only-compatible': False}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/storage/management/v1/bucket-definitions', params)
    buckets_json = json.loads(results.text)
    # print(buckets_json)

    buckets = buckets_json.get('buckets')

    print('bucketName', '|', 'table', '|', 'displayName')
    for bucket in buckets:
        print(bucket.get('bucketName'), '|', bucket.get('table'),  '|', bucket.get('displayName'))


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, client_id, client_secret)


if __name__ == '__main__':
    main()
