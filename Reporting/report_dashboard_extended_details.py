from Reuse import dynatrace_api
from Reuse import environment


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
    dashboards_json_list = dynatrace_api.get(env, token, endpoint, params)
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
            dashboard = dynatrace_api.get(env, token, endpoint, params)[0]
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
