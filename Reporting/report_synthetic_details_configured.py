import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []
    lines = []

    count_total = 0

    endpoint = '/api/v1/synthetic/monitors'
    params = ''
    entities_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)
    if print_mode:
        print('name' + '|' + 'entityId' + '|' + 'type' + '|' + 'enabled')
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('monitors')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            monitor_name = inner_entities_json.get('name')
            monitor_type = inner_entities_json.get('type')
            monitor_enabled = inner_entities_json.get('enabled')

            if print_mode:
                # print(monitor_name + '|' + entity_id + '|' + monitor_type + '|' + str(monitor_enabled))
                lines.append(monitor_name + '|' + entity_id + '|' + monitor_type + '|' + str(monitor_enabled))

            count_total += 1

    if print_mode:
        for line in sorted(lines):
            print(line)

    if print_mode:
        print('Total Synthetic Tests (Browser): ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' browser synthetic tests currently defined and reporting data.')

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