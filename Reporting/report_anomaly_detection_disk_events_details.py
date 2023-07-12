from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/anomalyDetection/diskEvents'
    params = ''
    anomaly_json = dynatrace_api.get(env, token, endpoint, params)[0]

    if print_mode:
        print('id' + '|' + 'name')

    anomaly_values = anomaly_json.get('values')
    for anomaly_value in anomaly_values:
        entity_id = anomaly_value.get('id')
        name = anomaly_value.get('name')
        if print_mode:
            print(entity_id + '|' + name)

        count_total += 1

    if print_mode:
        print('Total Anomaly Detection Disk Events: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' anomaly detection disk events currently defined.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def convert_boolean(boolean):
    if boolean:
        return 'on'
    else:
        return'off'
        

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
