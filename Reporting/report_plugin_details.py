from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/plugins'
    params = ''
    extension_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name' + '|' + 'description')

    for extension_json in extension_json_list:
        inner_extension_json_list = extension_json.get('values')
        for inner_extension_json in inner_extension_json_list:
            entity_id = inner_extension_json.get('id')
            name = inner_extension_json.get('name')
            description = inner_extension_json.get('description')

            if print_mode:
                print(entity_id + '|' + name + '|' + description)

            count_total += 1

    if print_mode:
        print('Total Plugins: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' plugins currently uploaded.')

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
