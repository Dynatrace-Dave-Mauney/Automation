from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    count_custom = 0

    endpoint = '/api/config/v1/extensions'
    params = 'pageSize=500'
    extension_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name' + '|' + 'type')

    for extension_json in extension_json_list:
        inner_extension_json_list = extension_json.get('extensions')
        for inner_extension_json in inner_extension_json_list:
            entity_id = inner_extension_json.get('id')
            name = inner_extension_json.get('name')
            entity_type = inner_extension_json.get('type')

            if print_mode:
                print(entity_id + '|' + name + '|' + entity_type)

            count_total += 1
            if not entity_id.startswith('dynatrace'):
                count_custom +=1

    if print_mode:
        print('Total Extensions:        ' + str(count_total))
        print('Total Custom Extensions: ' + str(count_custom))

    summary.append('There are ' + str(count_total) + ' extensions available. ' + 'There are ' + str(count_custom) + ' custom extensions currently available.')

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
