from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v1/oneagents'
    params = 'relativeTime=2hours'
    oneagents_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('entityId' + '|' + 'displayName' + '|' + 'discoveredName' + '|' + 'consumedHostUnits')

    for oneagents_json in oneagents_json_list:
        inner_oneagents_json_list = oneagents_json.get('hosts')
        for inner_oneagents_json in inner_oneagents_json_list:
            host_info = inner_oneagents_json.get('hostInfo')
            entity_id = host_info.get('entityId')
            display_name = host_info.get('displayName')
            discovered_name = host_info.get('discoveredName')
            consumed_host_units = host_info.get('consumedHostUnits')

            if print_mode:
                print(str(entity_id) + '|' + str(display_name) + '|' + str(discovered_name) + '|' + str(consumed_host_units))

            count_total += 1

    if print_mode:
        print('Total oneagents: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' oneagents.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def main():
    # env_name, env, token = environment.get_environment('Prod')
    env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    # env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
