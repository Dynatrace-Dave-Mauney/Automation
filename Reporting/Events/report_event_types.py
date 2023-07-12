from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/eventTypes'
    params = ''
    events_json_list = dynatrace_api.get(env, token, endpoint, params)
    # print(events_json_list)

    if print_mode:
        print('Event Types')
        print('id' + '|' + 'name')

    for events_json in events_json_list:
        inner_events_json_list = events_json.get('eventTypeInfos')
        for inner_events_json in inner_events_json_list:
            # print(inner_events_json)
            event_type = inner_events_json.get('type')
            display_name = inner_events_json.get('displayName')
            if print_mode:
                print(event_type + '|' + display_name)

            count_total += 1

    if print_mode:
        print('Total events: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' events currently defined.')

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
