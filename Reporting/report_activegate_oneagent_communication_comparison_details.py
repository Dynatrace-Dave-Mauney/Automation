from Reuse import dynatrace_api
from Reuse import environment

oneagent_communication_list = [
    '10.112.5.6',
    '10.118.65.148',
    '10.127.64.84',
    '10.131.11.0',
    '10.131.115.58',
    '10.131.116.134',
    '10.131.116.137',
    '10.131.118.118',
    '10.131.123.136',
    '10.131.151.56',
    '10.131.173.246',
    '10.131.182.126',
    '10.131.192.166',
    '10.131.197.196',
    '10.131.200.211',
    '10.131.206.253',
    '10.131.21.31',
    '10.131.228.254',
    '10.131.231.239',
    '10.131.233.87',
    '10.131.242.186',
    '10.131.34.165',
    '10.131.4.186',
    '10.131.57.98',
    '10.131.60.188',
    '10.131.61.217',
    '10.131.71.172',
    '10.131.8.175',
    '10.131.8.66',
    '10.131.93.132',
    '10.131.98.60',
    '10.20.172.187',
    '10.20.174.30',
    '10.20.175.223',
    '10.21.73.115',
    '10.247.244.32',
    'intxdc021v206.intprod.net',
    'lcq01751.live.dynatrace.com',
    'sg-us-west-2-34-211-171-253-prod-us-west-2-oregon.live.dynatrace.com',
    'sg-us-west-2-34-223-233-242-prod-us-west-2-oregon.live.dynatrace.com',
    'sg-us-west-2-35-155-216-1-prod-us-west-2-oregon.live.dynatrace.com',
    'sg-us-west-2-54-191-195-87-prod-us-west-2-oregon.live.dynatrace.com',
    'sg-us-west-2-54-191-195-87-prod-us-west-2-oregon.live.dynatrace.com',
    'sg-us-west-2-54-213-205-48-prod-us-west-2-oregon.live.dynatrace.com',
    'sg-us-west-2-54-213-211-21-prod-us-west-2-oregon.live.dynatrace.com',
    'td02a7ulcb-r00.cnb.corp.net',
    'tp041vcqkfh00.cnb.corp.net',
    'tp053b56v3n-agvm-nprd00.cnb.corp.net',
    'tp06vije-ir00.cnb.corp.net',
]

def process(env, token, print_mode):
    active_gate_network_address_list = []

    endpoint = '/api/v2/activeGates'
    params = ''
    activegates_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('ActiveGate network addresses not in OneAgent Communication List:')
        print('hostname' + '|' + 'osType' + '|' + 'version' + '|' + 'networkZone' + '|' + 'networkAddresses')

    for activegates_json in activegates_json_list:
        inner_activegates_json_list = activegates_json.get('activeGates')
        for inner_activegates_json in inner_activegates_json_list:
            # print(inner_activegates_json)
            entity_id = inner_activegates_json.get('id')
            os_type = inner_activegates_json.get('osType')
            version = inner_activegates_json.get('version')
            entity_type = inner_activegates_json.get('type')
            hostname = inner_activegates_json.get('hostname')
            environments = inner_activegates_json.get('environments')
            auto_update_settings = inner_activegates_json.get('autoUpdateSettings')
            network_zone = inner_activegates_json.get('networkZone')
            network_addresses = inner_activegates_json.get('networkAddresses')
            load_balancer_addresses = inner_activegates_json.get('loadBalancerAddresses')
            enabled_modules = []
            modules_list = inner_activegates_json.get('modules')
            for module in modules_list:
                if module.get("enabled"):
                    enabled_modules.append(module.get("type"))

            environments_str = stringify_list(environments)
            auto_update_settings_str = stringify_list(auto_update_settings)

            enabled_modules_str = str(enabled_modules).replace('[', '')
            enabled_modules_str = enabled_modules_str.replace(']', '')
            enabled_modules_str = enabled_modules_str.replace("'", "")

            found_in_oneagent_communication_list = False
            for network_address in network_addresses:
                if network_address not in active_gate_network_address_list:
                    active_gate_network_address_list.append(network_address)
                if network_address in oneagent_communication_list:
                    found_in_oneagent_communication_list = True
                    break

            if found_in_oneagent_communication_list:
                continue

            # if print_mode:
            #     print(hostname + '|' + os_type + '|' + version + '|' + entity_type + '|' + hostname + '|' + environments_str + '|' + auto_update_settings_str + '|' + network_zone + '|' + enabled_modules_str)
            if 'ONE_AGENT_ROUTING' and print_mode and not 'aks' in hostname and not 'SYNTHETIC' in enabled_modules_str:
                print(hostname + '|' + os_type + '|' + version + '|' + network_zone + '|' + stringify_list(network_addresses))

    print('')
    print('OneAgent Communication List Entries not found in the ActiveGate network address list:')
    for oneagent_communication in oneagent_communication_list:
        if oneagent_communication not in active_gate_network_address_list:
            if not oneagent_communication.endswith('dynatrace.com'):
                print(oneagent_communication)

    print('')
    print('OneAgent Communication List:')
    print(sorted(oneagent_communication_list))

    print('')
    print('ActiveGate Network Address List:')
    print(sorted(active_gate_network_address_list))


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def stringify_list(any_list):
    any_list_string = str(any_list)
    any_list_string = any_list_string.replace('[', '')
    any_list_string = any_list_string.replace(']', '')
    any_list_string = any_list_string.replace("'", "")
    return any_list_string


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token, True)


if __name__ == '__main__':
    main()
