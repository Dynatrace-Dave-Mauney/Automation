"""
Refresh ServiceNow JWT Token for each problem notification integration specified.
"""
import base64
import json

from Reuse import dynatrace_api
from Reuse import environment


endpoint = '/api/config/v1/notifications'
service_now_problem_notification_ids = {
    'Prod': [],
    'PreProd': [],
    'Dev': ['1fdd88eb-f9ae-37c5-8267-da088ec2e8f5'],
    'Sandbox': [],
}


def process(env_name, env, token):
    get_jwt()

    service_now_problem_notification_id_list = service_now_problem_notification_ids.get(env_name, [])
    for service_now_problem_notification_id in service_now_problem_notification_id_list:
        url = f'{env}{endpoint}/{service_now_problem_notification_id}'
        r = dynatrace_api.get_without_pagination(url, token)
        service_now_problem_notification = r.json()
        header_list = service_now_problem_notification.get('headers', {})
        header_index = 0
        for header in header_list:
            name = header.get('name')
            if name == 'Authorization':
                header['value'] = service_now_problem_notification_id
                header_list[header_index] = header
                service_now_problem_notification['headers'] = header_list
                dynatrace_api.put_object(url, token, json.dumps(service_now_problem_notification))
            header_index += 1


def get_jwt():
    service_now_url = 'https://odfldev.service-now.com/oauth_token.do'
    service_now_jwt_header = {'kid': 'fcc2c3ab7ec8825057c25624b011dc73'}
    service_now_jwt_payload = {'aud': '6b500fa724c8825075f56f3fbb2be758', 'iss': '6b500fa724c8825075f56f3fbb2be758', 'sub': 'dynatracedev@odfl.com'}
    service_now_jwt_provider_sysid = '1c39cfe3970c825013e6f0cfe153af7f'

    service_now_jwt_header_base64_string = get_base64_encoded_string(service_now_jwt_header)
    service_now_jwt_payload_base64_string = get_base64_encoded_string(service_now_jwt_payload)

    exit(1234)


def get_base64_encoded_string(input):
    input_string = str(input)
    input_string_bytes = input_string.encode('ascii')
    input_string_base64_bytes = base64.b64encode(input_string_bytes)
    input_string_base64_string = input_string_base64_bytes.decode('ascii')
    print(f"Encoded string: {input_string_base64_string}")
    return input_string_base64_string


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env_name, env, token)


if __name__ == '__main__':
    main()
