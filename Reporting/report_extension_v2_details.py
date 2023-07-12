from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/extensions'
    params = 'pageSize=100'
    extension_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('extensionName' + '|' + 'version')

    for extension_json in extension_json_list:
        inner_extension_json_list = extension_json.get('extensions')
        for inner_extension_json in inner_extension_json_list:
            extension_name = inner_extension_json.get('extensionName')
            version = inner_extension_json.get('version')

            if print_mode:
                print(extension_name + '|' + version)

            count_total += 1

    if print_mode:
        print('Total Extensions 2.0: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' extensions 2.0 currently available.')

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
