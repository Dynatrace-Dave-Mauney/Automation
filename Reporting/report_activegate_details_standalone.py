from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/activeGates'
    params = ''
    activegates_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'osType' + '|' + 'version' + '|' + 'type' + '|' + 'hostname' + '|' + 'environments' + '|' + 'autoUpdateSettings' + '|' + 'networkZone' + '|' + 'modules' + '|' + 'networkAddresses')

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
            enabled_modules = []
            modules_list = inner_activegates_json.get('modules')
            for module in modules_list:
                if module.get("enabled"):
                    enabled_modules.append(module.get("type"))
            network_addresses = inner_activegates_json.get('networkAddresses')

            environments_str = str(environments).replace('[', '')
            environments_str = environments_str.replace(']', '')
            environments_str = environments_str.replace("'", "")

            auto_update_settings_str = str(auto_update_settings).replace('{', '')
            auto_update_settings_str = auto_update_settings_str.replace('}', '')
            auto_update_settings_str = auto_update_settings_str.replace("'", "")

            enabled_modules_str = str(enabled_modules).replace('[', '')
            enabled_modules_str = enabled_modules_str.replace(']', '')
            enabled_modules_str = enabled_modules_str.replace("'", "")

            if print_mode:
                print(entity_id + '|' + os_type + '|' + version + '|' + entity_type + '|' + hostname + '|' + environments_str + '|' + auto_update_settings_str + '|' + network_zone + '|' + enabled_modules_str + '|' + str(network_addresses))

            if 'ONE_AGENT_ROUTING' in enabled_modules and \
                    ('AWS' in enabled_modules or
                     'AZURE' in enabled_modules or
                     'VMWARE' in enabled_modules or
                     'EXTENSIONS_V1' in enabled_modules or
                     'EXTENSIONS_V2' in enabled_modules):
                summary.append('ActiveGate is configured for OneAgent routing and running extensions on ' + hostname)
                # print(sorted(enabled_modules))

            count_total += 1

    if print_mode:
        print('Total activegates: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' activegates currently defined and reporting.')

    if print_mode:
        print_list(sorted(summary))
        print('Done!')

    return sorted(summary)


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
