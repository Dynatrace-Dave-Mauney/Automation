import dynatrace_rest_api_helper
import os


friendly_type_name = {'processGroup': 'process groups', 'host': 'hosts', 'service': 'services'}


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    if print_mode:
        print('id' + '|' + 'name')

    summary.append(process_type(env, token, print_mode, 'processGroup')[0])
    summary.append(process_type(env, token, print_mode, 'host')[0])
    summary.append(process_type(env, token, print_mode, 'service')[0])

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def process_type(env, token, print_mode, entity_type):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/conditionalNaming/' + entity_type
    params = ''
    conditional_naming_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)

    for conditional_naming_json in conditional_naming_json_list:
        inner_conditional_naming_json_list = conditional_naming_json.get('values')
        for inner_conditional_naming_json in inner_conditional_naming_json_list:
            entity_id = inner_conditional_naming_json.get('id')
            name = inner_conditional_naming_json.get('name')

            if print_mode:
                print(entity_id + '|' + name)

            count_total += 1

    if print_mode:
        print('Total Conditional Naming Rules - ' + friendly_type_name[entity_type] + ': ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' conditional naming rules for ' + friendly_type_name[entity_type] + ' currently defined.')

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
