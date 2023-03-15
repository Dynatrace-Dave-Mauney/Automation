from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/networkZones'
    params = ''
    network_zones_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'description' + '|' + 'alternativeZones' + '|' + 'numOfOneAgentsUsing' + '|' + 'numOfConfiguredOneAgents' + '|' + 'numOfOneAgentsFromOtherZones' + '|' + 'numOfConfiguredActiveGates')

    for network_zones_json in network_zones_json_list:
        inner_network_zones_json_list = network_zones_json.get('networkZones')
        for inner_network_zones_json in inner_network_zones_json_list:
            entity_id = inner_network_zones_json.get('id')
            description = inner_network_zones_json.get('description')
            alternative_zones = inner_network_zones_json.get('alternativeZones')
            # version = inner_network_zones_json.get('version')
            num_of_one_agents_using = inner_network_zones_json.get('numOfOneAgentsUsing')
            num_of_configured_one_agents = inner_network_zones_json.get('numOfConfiguredOneAgents')
            num_of_one_agents_from_other_zones = inner_network_zones_json.get('numOfOneAgentsFromOtherZones')
            num_of_configured_active_gates = inner_network_zones_json.get('numOfConfiguredActiveGates')

            alternative_zones_str = str(alternative_zones).replace('[', '')
            alternative_zones_str = alternative_zones_str.replace(']', '')
            alternative_zones_str = alternative_zones_str.replace("'", "")

            if print_mode:
                print(entity_id + '|' + description + '|' + alternative_zones_str + '|' + str(num_of_one_agents_using) + '|' + str(num_of_configured_one_agents) + '|' + str(num_of_one_agents_from_other_zones) + '|' + str(num_of_configured_active_gates))

            count_total += 1

    if print_mode:
        print('Total network_zones: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' network zones currently defined and reporting.')

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
