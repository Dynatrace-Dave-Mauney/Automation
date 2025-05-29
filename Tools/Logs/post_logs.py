import json

from Reuse import dynatrace_api
from Reuse import environment


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

    log_payload = generate_log_payload()
    formatted_log_payload = json.dumps(log_payload, indent=4, sort_keys=False)

    response = dynatrace_api.post_object(f'{env}{endpoint}', token, formatted_log_payload)

    print(f'Posted log payload to {env_name} ({env}) with response: {response}')
    print(f'{response.text}')
    print('')


def generate_log_payload():
    log_payload_list = []
    log_playload_dict1 = {}
    log_playload_dict2 = {}

    log_playload_dict1['content'] = 'Test Payload 500 Format 1'
    log_playload_dict2['content'] = 'Test Payload 500 Format 2'

    log_playload_dict2['attributes'] = {}

    attribute_number = 1

    for i in range(500):
        attribute_key = str(i + 1)
        attribute_value = str(i + 1)
        # print(attribute_key, attribute_value)
        log_playload_dict1[attribute_key] = attribute_value
        log_playload_dict2['attributes'][attribute_key] = attribute_value

    print(log_playload_dict1)
    print(log_playload_dict2)

    log_payload_list.append(log_playload_dict1)
    log_payload_list.append(log_playload_dict2)

    print(log_payload_list)

    return log_payload_list


def main():
    process()


if __name__ == '__main__':
    main()
