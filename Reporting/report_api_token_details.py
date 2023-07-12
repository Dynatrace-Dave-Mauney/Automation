from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/apiTokens'
    params = ''
    activegates_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name' + '|' + 'enabled' + '|' + 'owner' + '|' + 'creationDate')

    for activegates_json in activegates_json_list:
        inner_activegates_json_list = activegates_json.get('apiTokens')
        for inner_activegates_json in inner_activegates_json_list:
            entity_id = inner_activegates_json.get('id')
            name = inner_activegates_json.get('name')
            enabled = inner_activegates_json.get('enabled')
            owner = inner_activegates_json.get('owner')
            creation_date = inner_activegates_json.get('creationDate')

            if print_mode:
                print(entity_id + '|' + name + '|' + str(enabled) + '|' + owner + '|' + creation_date)

            count_total += 1

    if print_mode:
        print('Total API Tokens: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' API tokens currently available.')

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
