import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/apiTokens'
    params = ''
    activegates_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)

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
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, True)


if __name__ == '__main__':
    # print('Not to be run standalone.  Use one of the "perform_*.py" modules to run this module.')
    # exit(1)
    main()
