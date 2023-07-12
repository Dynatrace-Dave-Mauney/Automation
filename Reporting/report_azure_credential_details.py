from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/azure/credentials'
    params = ''
    azure_credentials_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name')

    for azure_credentials_json in azure_credentials_json_list:
        inner_azure_credentials_json_list = azure_credentials_json.get('values')
        for inner_azure_credentials_json in inner_azure_credentials_json_list:
            entity_id = inner_azure_credentials_json.get('id')
            name = inner_azure_credentials_json.get('name')

            if print_mode:
                print(entity_id + '|' + name)

            count_total += 1

    if print_mode:
        print('Total azure subscriptions: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' azure subscriptions currently configured.')

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
