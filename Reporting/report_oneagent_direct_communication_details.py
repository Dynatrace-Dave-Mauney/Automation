from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v1/oneagents'
    params = 'activeGateId=DIRECT_COMMUNICATION&relativeTime=2hours'
    oneagents_json_list = dynatrace_api.get(env, token, endpoint, params)

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
