import json

from Reuse import dynatrace_api
from Reuse import environment


import copy


def process():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Prod'
    env_name_supplied = 'Personal'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    endpoint = '/api/v2/logs/ingest'

    log_payload = load_log_payload()
    formatted_log_payload = json.dumps(log_payload, indent=4, sort_keys=False)

    response = dynatrace_api.post_object(f'{env}{endpoint}', token, formatted_log_payload)

    print(f'Posted log payload to {env_name} ({env})')
    print('')


def load_log_payload():
    with open('log_payload.json', 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def main():
    process()


if __name__ == '__main__':
    main()
