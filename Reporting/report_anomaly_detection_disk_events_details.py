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
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
