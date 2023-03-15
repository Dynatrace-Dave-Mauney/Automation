from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/kubernetes/credentials'
    params = ''
    kubernetes_credentials_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name' + '|' + 'endpointUrl' + '|' + 'eventsIntegrationEnabled')

    events_not_enabled = []

    for kubernetes_credentials_json in kubernetes_credentials_json_list:
        inner_kubernetes_credentials_json_list = kubernetes_credentials_json.get('values')
        for inner_kubernetes_credentials_json in inner_kubernetes_credentials_json_list:
            entity_id = inner_kubernetes_credentials_json.get('id')
            name = inner_kubernetes_credentials_json.get('name')
            endpoint_url = inner_kubernetes_credentials_json.get('endpointUrl')

            endpoint = '/api/config/v1/kubernetes/credentials/' + entity_id
            params = ''
            details = dynatrace_api.get(env, token, endpoint, params)[0]

            events_integration_enabled = details.get('eventsIntegrationEnabled')

            if not events_integration_enabled:
                events_not_enabled.append(name)

            if print_mode:
                print(entity_id + '|' + name + '|' + endpoint_url + ' |' + str(events_integration_enabled))

            count_total += 1

    if print_mode:
        print('Total Kubernetes Clusters: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' kubernetes clusters currently configured.')

    if count_total > 0:
        if len(events_not_enabled) > 0:
            events_not_enabled_string = str(events_not_enabled)
            events_not_enabled_string = events_not_enabled_string.replace('[', '')
            events_not_enabled_string = events_not_enabled_string.replace(']', '')
            events_not_enabled_string = events_not_enabled_string.replace("'", "")
            summary.append('The following ' + str(len(events_not_enabled)) + ' clusters do not have events integration enabled: ' + events_not_enabled_string)
        else:
            summary.append('All kubernetes clusters have events integration enabled as per expectations.')

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
