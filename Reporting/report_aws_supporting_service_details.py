from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/aws/supportedServices'
    params = ''
    aws_supported_services_json_dict = dynatrace_api.get(env, token, endpoint, params)[0]
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
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token, True)
    
    
if __name__ == '__main__':
    main()
