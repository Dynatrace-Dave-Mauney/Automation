import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v1/oneagents'
    params = 'activeGateId=DIRECT_COMMUNICATION&relativeTime=2hours'
    oneagents_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)

    if print_mode:
        print('entityId' + '|' + 'displayName' + '|' + 'discoveredName')

    for oneagents_json in oneagents_json_list:
        inner_oneagents_json_list = oneagents_json.get('hosts')
        for inner_oneagents_json in inner_oneagents_json_list:
            host_info = inner_oneagents_json.get('hostInfo')
            entity_id = host_info.get('entityId')
            display_name = host_info.get('displayName')
            discovered_name = host_info.get('discoveredName')

            if print_mode:
                print(str(entity_id) + '|' + str(display_name) + '|' + str(discovered_name))

            count_total += 1

    if print_mode:
        print('Total oneagents in direct communication with the Dynatrace cluster: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' oneagents in direct communication with the Dynatrace cluster.')

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
