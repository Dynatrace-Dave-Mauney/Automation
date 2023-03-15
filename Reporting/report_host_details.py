import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    count_full_stack = 0
    count_infra_only = 0

    counts_os = {}
    counts_state = {}
    counts_network_zone = {}
    counts_hypervisor_type = {}

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    if print_mode:
        print('entityId' + '|' + 'displayName' + '|' + 'monitoringMode' + '|' + 'logicalCpuCores' + '|' + 'cpuCores' + '|' + 'memoryTotal' + '|' + 'osType' + '|' + 'state' + '|' + 'networkZone' + '|' + 'hypervisorType' + '|' + 'cloudType' + '|' + 'k8sCluster' + '|' + 'environment' + '|' + 'dataCenter')
        # print('entityId' + '|' + 'displayName' + '|' + 'tags')
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')

            properties = inner_entities_json.get('properties')

            monitoring_mode = properties.get('monitoringMode', '')
            logical_cpu_cores = str(properties.get('logicalCpuCores', ''))
            cpu_cores = str(properties.get('cpuCores', ''))
            memory_total = str(properties.get('memoryTotal', ''))
            os_type = properties.get('osType', '')
            state = properties.get('state', 'NONE')
            network_zone = properties.get('networkZone', 'NONE')
            hypervisor_type = properties.get('hypervisorType', 'NONE')
            cloud_type = properties.get('cloudType', 'On Premise')
            tags = inner_entities_json.get('tags', [])
            k8s_cluster = ''
            environment = ''
            data_center = ''
            for tag in tags:
                # print(tag)
                if "Kubernetes Cluster" in str(tag):
                    k8s_cluster = tag.get('value', '')
                if "Environment" in str(tag):
                    environment = tag.get('value', '')
                if "Data Center" in str(tag):
                    data_center = tag.get('value', '')

            if print_mode:
                print(entity_id + '|' + display_name + '|' + monitoring_mode + '|' + logical_cpu_cores + '|' +
                      cpu_cores + '|' + memory_total + '|' + os_type + '|' + state + '|' + network_zone + '|' +
                      hypervisor_type + '|' + cloud_type + '|' + k8s_cluster + '|' + environment + '|' + data_center)
                # Temp code: for listing hosts and their host groups only
                # for tag in tags:
                #     # print(tag)
                #     if "Host Group" in str(tag):
                #         host_group = tag.get('value', None)
                #         # print(host_group)
                #         if host_group:
                #             print(entity_id + '|' + display_name + '|' + host_group)
                #         continue

            count_total += 1

            if monitoring_mode == 'FULL_STACK':
                count_full_stack += 1
            if monitoring_mode == 'INFRASTRUCTURE':
                count_infra_only += 1

            counts_os[os_type] = counts_os.get(os_type, 0) + 1
            counts_state[state] = counts_state.get(state, 0) + 1
            counts_network_zone[network_zone] = counts_network_zone.get(network_zone, 0) + 1
            counts_hypervisor_type[hypervisor_type] = counts_hypervisor_type.get(hypervisor_type, 0) + 1

    # counts_os_str = str(counts_os).replace('{', '').replace("'", "").replace('}', '')
    # counts_hypervisor_type_str = str(counts_hypervisor_type).replace('{', '').replace("'", "").replace('}', '')
    # counts_network_zone_str = str(counts_network_zone).replace('{', '').replace("'", "").replace('}', '')
    # counts_state_str = str(counts_state).replace('{', '').replace("'", "").replace('}', '')

    counts_os_str = sort_and_stringify_dictionary_items(counts_os)
    counts_hypervisor_type_str = sort_and_stringify_dictionary_items(counts_hypervisor_type)
    counts_network_zone_str = sort_and_stringify_dictionary_items(counts_network_zone)
    counts_state_str = sort_and_stringify_dictionary_items(counts_state)

    if print_mode:
        print('Total Hosts:            ' + str(count_total))
        print('Full Stack:             ' + str(count_full_stack))
        print('Infra Only:             ' + str(count_infra_only))
        print('OS Counts:              ' + counts_os_str)
        print('Hypervisor Type Counts: ' + counts_hypervisor_type_str)
        print('Network Zone Counts:    ' + counts_network_zone_str)
        print('State Counts:           ' + counts_state_str)

    summary.append('There are ' + str(count_total) + ' hosts currently being monitored.  ')
    if count_total > 0:
        summary.append(str(count_full_stack) + ' hosts are being monitored in full stack mode and ' +
            str(count_infra_only) + ' hosts are being monitored in infrastructure only mode. ' +
            'The operating systems breakdown is ' + counts_os_str + '.  ' +
            'The Hypervisor breakdown is ' + counts_hypervisor_type_str + '.  ' +
            'The Network Zone breakdown is ' + counts_network_zone_str + '.  ' +
            'The Agent State breakdown is ' + counts_state_str + '.  ')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def sort_and_stringify_dictionary_items(any_dict):
    dict_str = str(sorted(any_dict.items()))
    dict_str = dict_str.replace('[', '')
    dict_str = dict_str.replace(']', '')
    dict_str = dict_str.replace('), (', '~COMMA~')
    dict_str = dict_str.replace('(', '')
    dict_str = dict_str.replace(')', '')
    dict_str = dict_str.replace(',', ':')
    dict_str = dict_str.replace('~COMMA~', ', ')
    dict_str = dict_str.replace("'", "")
    return dict_str


def main():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
