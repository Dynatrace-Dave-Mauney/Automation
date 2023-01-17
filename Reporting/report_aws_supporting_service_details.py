import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/aws/supportedServices'
    params = ''
    aws_supported_services_json_dict = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]
    aws_supported_services_json_list = aws_supported_services_json_dict.get('services')

    if print_mode:
        print('displayName')

    lines = []
    for aws_supported_services_json in aws_supported_services_json_list:
        # entity_type = aws_supported_services_json.get('entityType')
        display_name = aws_supported_services_json.get('displayName')

        if print_mode:
            lines.append(display_name)

        count_total += 1

    if print_mode:
        for line in sorted(lines):
            print(line)
        print('Total AWS Supported Services: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' AWS supported services present.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)
        

def main():
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, True)


if __name__ == '__main__':
    main()
