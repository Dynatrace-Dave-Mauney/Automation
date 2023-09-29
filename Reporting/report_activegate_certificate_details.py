# TODO: Test: This module is only partially complete and has not yet
#               been tested due to empty result list with personal tenant
# TODO: Report Upgrade

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

def summarize(env, token):
    return process(env, token)


def process(token, print_mode):
    summary = []

    count_total = 0

    tenant = environment.get_configuration('report_activegate_certificate_details.temp_tenant')

    # curl https://{address of ActiveGate}:{port}/e/{environment ID}/api/v1/certificate/{certificate file name} -H"Authorization: Api-Token {token}" -H"X-Password: {password}" -T {path to certificate file}
    # https://www.dynatrace.com/support/help/shortlink/activegate-configuration-ssl#managing-certificates-via-rest-api
    # List:
    # https://myActiveGate:9999/e/myEnvironmentId/api/v1/certificate/list
    # endpoint = f'https://localhost:9999/e/{tenant}/api/v1/certificate/list'
    endpoint = f'https://localhost:9999/e/{tenant}/api/v1/certificate/list'
    params = ''
    activegates_json_list = dynatrace_api.get(endpoint, token, endpoint, params)
    print(activegates_json_list)

    # if print_mode:
    #     print('id' + '|' + 'osType' + '|' + 'version' + '|' + 'type' + '|' + 'hostname' + '|' + 'environments' + '|' + 'autoUpdateSettings' + '|' + 'networkZone' + '|' + 'modules')
    if print_mode:
        print('hostname' + '|' + 'osType' + '|' + 'version' + '|' + 'networkZone' + '|' + 'networkAddresses')

    for activegates_json in activegates_json_list:
        inner_activegates_json_list = activegates_json.get('activeGates')
        for inner_activegates_json in inner_activegates_json_list:
            print(inner_activegates_json)
            # entity_id = inner_activegates_json.get('id')
            os_type = inner_activegates_json.get('osType')
            version = inner_activegates_json.get('version')
            # entity_type = inner_activegates_json.get('type')
            hostname = inner_activegates_json.get('hostname')
            # environments = inner_activegates_json.get('environments')
            # auto_update_settings = inner_activegates_json.get('autoUpdateSettings')
            network_zone = inner_activegates_json.get('networkZone')
            network_addresses = inner_activegates_json.get('networkAddresses')
            # load_balancer_addresses = inner_activegates_json.get('loadBalancerAddresses')
            enabled_modules = []
            modules_list = inner_activegates_json.get('modules')
            for module in modules_list:
                if module.get("enabled"):
                    enabled_modules.append(module.get("type"))

            # environments_str = report_writer.stringify_list(environments)
            # auto_update_settings_str = report_writer.stringify_list(auto_update_settings)

            enabled_modules_str = str(enabled_modules).replace('[', '')
            enabled_modules_str = enabled_modules_str.replace(']', '')
            enabled_modules_str = enabled_modules_str.replace("'", "")

            # if print_mode:
            #     print(hostname + '|' + os_type + '|' + version + '|' + entity_type + '|' + hostname + '|' + environments_str + '|' + auto_update_settings_str + '|' + network_zone + '|' + enabled_modules_str)
            if 'ONE_AGENT_ROUTING' and print_mode and 'aks' not in hostname and 'SYNTHETIC' not in enabled_modules_str:
                # print(inner_activegates_json)
                print(hostname + '|' + os_type + '|' + version + '|' + network_zone + '|' + report_writer.stringify_list(network_addresses))

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
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    # env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    token = environment.get_configuration('report_activegate_certificate_details.temp_token')
    print(token)
    process(token, True)


if __name__ == '__main__':
    main()
