from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    count_enabled = 0
    count_disabled = 0

    endpoint = '/api/config/v1/maintenanceWindows'
    params = ''
    maintenance_windows_json_list = dynatrace_api.get(env, token, endpoint, params)

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
            maintenance_window = dynatrace_api.get(env, token, endpoint, params)[0]
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

    summary.append('There are ' + str(count_total) + ' maintenance windows currently defined.')
    if count_total > 0:
        summary.append(str(count_enabled) + ' are currently enabled and ' + str(count_disabled) + ' are currently disabled.')

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
