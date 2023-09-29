from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    report_name = 'ActiveGate Details'
    rows = []
    summary = []

    count_total = 0

    endpoint = '/api/v2/activeGates'
    params = ''
    activegates_json_list = dynatrace_api.get(env, token, endpoint, params)

    for activegates_json in activegates_json_list:
        inner_activegates_json_list = activegates_json.get('activeGates')
        for inner_activegates_json in inner_activegates_json_list:
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

            environments_str = report_writer.stringify_list(environments)
            auto_update_settings_str = report_writer.stringify_list(auto_update_settings)

            enabled_modules_str = str(enabled_modules).replace('[', '')
            enabled_modules_str = enabled_modules_str.replace(']', '')
            enabled_modules_str = enabled_modules_str.replace("'", "")

            if not summary_mode:
                rows.append((hostname, entity_id, os_type, version, network_zone, report_writer.stringify_list(network_addresses), report_writer.stringify_list(load_balancer_addresses), entity_type,  environments_str, auto_update_settings_str, enabled_modules_str))

            # One-off
            # if 'ONE_AGENT_ROUTING' and summary_mode and not 'aks' in hostname and not 'SYNTHETIC' in enabled_modules_str:
            #     print(hostname + '|' + os_type + '|' + version + '|' + network_zone + '|' + report_writer.stringify_list(network_addresses))

            if 'ONE_AGENT_ROUTING' in enabled_modules and \
                    ('AWS' in enabled_modules or
                     'AZURE' in enabled_modules or
                     'VMWARE' in enabled_modules or
                     'EXTENSIONS_V1' in enabled_modules or
                     'EXTENSIONS_V2' in enabled_modules):
                summary.append('ActiveGate is configured for OneAgent routing and running extensions on ' + hostname)

            count_total += 1

    summary.append('There are ' + str(count_total) + ' ActiveGates currently defined and reporting.')

    if not summary_mode:
        report_writer.initialize_text_file(None)
        report_headers = ('hostname', 'id', 'osType', 'version', 'networkZone', 'networkAddresses', 'loadBalancerAddresses', 'type', 'environments', 'autoUpdateSettings', 'enabledModules')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total ActiveGates: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return sorted(summary)


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
