import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    count_shared = 0
    count_preset = 0
    count_dynatrace_owned = 0

    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboards_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)
    # print(dashboards_json_list)

    if print_mode:
        print('id' + '|' + 'name' + '|' + 'owner' + '|' + 'shared' + '|' + 'preset')

    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')
            name = inner_dashboards_json.get('name')
            owner = inner_dashboards_json.get('owner')

            endpoint = '/api/config/v1/dashboards/' + entity_id
            params = ''
            dashboard = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]
            dashboard_metadata = dashboard.get('dashboardMetadata')
            shared = dashboard_metadata.get('shared', False)
            preset = dashboard_metadata.get('preset', False)

            if print_mode:
                print(entity_id + '|' + name + '|' + owner + '|' + str(shared) + '|' + str(preset))

            count_total += 1
            if shared:
                count_shared += 1
            if preset:
                count_preset += 1
            if owner == 'Dynatrace':
                count_dynatrace_owned += 1

    if print_mode:
        print('Total Dashboards:   ' + str(count_total))
        print('Shared:             ' + str(count_shared))
        print('Preset:             ' + str(count_preset))
        print('Dynatrace Created:  ' + str(count_dynatrace_owned))

    summary.append('There are ' + str(count_total) + ' dashboards currently defined.  ' +
                   str(count_shared) + ' are currently shared. ' + str(count_preset) + ' are defined as preset. ' + str(count_dynatrace_owned) + ' were created by Dynatrace.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def main():
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')
    env_name, tenant_key, token_key = ('FreeTrial1', 'FREETRIAL1_TENANT', 'ROBOT_ADMIN_FREETRIAL1_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, True)


if __name__ == '__main__':
    # print('Not to be run standalone.  Use one of the "perform_*.py" modules to run this module.')
    # exit(1)
    main()
