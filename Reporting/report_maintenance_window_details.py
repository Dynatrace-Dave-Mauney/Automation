import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    count_enabled = 0
    count_disabled = 0

    endpoint = '/api/config/v1/maintenanceWindows'
    params = ''
    maintenance_windows_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name' + '|' + 'description' + '|' + 'type' + '|' + 'enabled' + '|' + 'suppression' + '|' + 'suppressSyntheticMonitorsExecution')

    for maintenance_windows_json in maintenance_windows_json_list:
        inner_maintenance_windows_json_list = maintenance_windows_json.get('values')
        for inner_maintenance_windows_json in inner_maintenance_windows_json_list:
            entity_id = inner_maintenance_windows_json.get('id')
            name = inner_maintenance_windows_json.get('name')
            description = inner_maintenance_windows_json.get('description', '')

            endpoint = '/api/config/v1/maintenanceWindows/' + entity_id
            params = ''
            maintenance_window = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]
            entity_type = maintenance_window.get('type', '')
            enabled = maintenance_window.get('enabled', '')
            suppression = maintenance_window.get('suppression', '')
            suppress_synthetic_monitors_execution = maintenance_window.get('suppressSyntheticMonitorsExecution', '')

            if print_mode:
                print(entity_id + '|' + name + '|' + description + '|' + description + '|' + entity_type + '|' + str(enabled) + '|' + suppression + '|' + str(suppress_synthetic_monitors_execution))

            count_total += 1

            if enabled:
                count_enabled += 1
            else:
                count_disabled += 1

    if print_mode:
        print('Total Maintenance Windows:    ' + str(count_total))
        print('Enabled Maintenance Windows:  ' + str(count_enabled))
        print('Disabled Maintenance Windows: ' + str(count_disabled))

    summary.append('There are ' + str(count_total) + ' maintenance windows currently defined.  ' + str(count_enabled) +
                   ' are currently enabled and ' + str(count_disabled) + ' are currently disabled.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        line = line.replace('.  0 are', '.  None are')
        line = line.replace(' 0 are', ' none are')
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
