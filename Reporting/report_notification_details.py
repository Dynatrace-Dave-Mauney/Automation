from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/notifications'
    params = ''
    notifications_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name')

    for notifications_json in notifications_json_list:
        inner_notifications_json_list = notifications_json.get('values')
        for inner_notifications_json in inner_notifications_json_list:
            entity_id = inner_notifications_json.get('id')
            name = inner_notifications_json.get('name')

            # for later if details of rules, etc. are needed from each notification...
            # endpoint = '/api/config/v1/notifications/' + entity_id
            # params = ''
            # notification = dynatrace_api.get(env, token, endpoint, params)[0]

            if print_mode:
                print(entity_id + '|' + name)

            count_total += 1

    if print_mode:
        print('Total Notifications: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' notifications currently defined.')

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
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
