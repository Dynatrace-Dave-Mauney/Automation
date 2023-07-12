from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/autoTags'
    params = ''
    autotags_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name')

    for autotags_json in autotags_json_list:
        inner_autotags_json_list = autotags_json.get('values')
        for inner_autotags_json in inner_autotags_json_list:
            entity_id = inner_autotags_json.get('id')
            name = inner_autotags_json.get('name')

            # for later if details of rules, etc. are needed from each autotag...
            # endpoint = '/api/config/v1/autoTags/' + id
            # params = ''
            # autotag = dynatrace_api.get(env, token, endpoint, params)[0]

            if print_mode:
                print(entity_id + '|' + name)

            count_total += 1

    if print_mode:
        print('Total Automatically Applied Tags: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' automatically applied tags currently defined.')

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
