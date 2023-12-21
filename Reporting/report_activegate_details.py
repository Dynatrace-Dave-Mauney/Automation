import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    cluster_version = get_cluster_version(env, token)
    cluster_version_split = cluster_version.split('.')
    cluster_minor_version = cluster_version_split[1]

    active_gate_auto_update_setting = get_active_gate_auto_update_setting(env, token)

    rows = []
    summary = []

    count_total = 0
    count_version_up_to_date = 0
    count_version_not_up_to_date = 0
    max_version = 0
    min_version = 0

    endpoint = '/api/v2/activeGates'
    activegates_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for activegates_json in activegates_json_list:
        inner_activegates_json_list = activegates_json.get('activeGates')
        for inner_activegates_json in inner_activegates_json_list:
            entity_id = inner_activegates_json.get('id')
            os_type = inner_activegates_json.get('osType')
            version = inner_activegates_json.get('version')

            version_status = 'N/A'
            active_gate_version_split = version.split('.')
            active_gate_minor_version = active_gate_version_split[1]
            if int(active_gate_minor_version) < int(cluster_minor_version) - 2:
                version_status = 'Not Up To Date'
                count_version_not_up_to_date += 1
            else:
                version_status = 'Up To Date'
                count_version_up_to_date += 1

            if int(active_gate_minor_version) > max_version:
                max_version = int(active_gate_minor_version)

            if int(active_gate_minor_version) < min_version or min_version == 0:
                min_version = int(active_gate_minor_version)

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
                rows.append((hostname, entity_id, os_type, version, version_status, network_zone, report_writer.stringify_list(network_addresses), report_writer.stringify_list(load_balancer_addresses), entity_type,  environments_str, auto_update_settings_str, enabled_modules_str))

            # One-off
            # if 'ONE_AGENT_ROUTING' and summary_mode and not 'aks' in hostname and not 'SYNTHETIC' in enabled_modules_str:
            #     print(hostname + '|' + os_type + '|' + version + '|' + network_zone + '|' + report_writer.stringify_list(network_addresses))

            if 'ONE_AGENT_ROUTING' in enabled_modules and \
                    ('AWS' in enabled_modules or
                     'AZURE' in enabled_modules or
                     'VMWARE' in enabled_modules or
                     'EXTENSIONS_V1' in enabled_modules or
                     'EXTENSIONS_V2' in enabled_modules):
                summary.append(f'ActiveGate is configured for OneAgent routing and running extensions on {hostname} ({report_writer.stringify_list(network_addresses)})')
            else:
                if (
                    'AWS' in enabled_modules or
                    'AZURE' in enabled_modules or
                    'VMWARE' in enabled_modules or
                    'EXTENSIONS_V1' in enabled_modules or
                    'EXTENSIONS_V2' in enabled_modules
                ):
                    summary.append('ActiveGate is configured for running extensions on ' + hostname)

            count_total += 1

    summary.append('There are ' + str(count_total) + ' ActiveGates currently defined and reporting.')

    summary.append('There are ' + str(count_version_not_up_to_date) + ' ActiveGates that are not up to date.')
    summary.append('There are ' + str(count_version_up_to_date) + ' ActiveGates that are up to date.')
    summary.append('The newest minor version is ' + str(max_version))
    summary.append('The oldest minor version is ' + str(min_version))
    summary.append('ActiveGate automatic update setting is ' + str(active_gate_auto_update_setting))

    if not summary_mode:
        report_writer.initialize_text_file(None)
        report_name = 'ActiveGate Details'
        report_headers = ('hostname', 'id', 'osType', 'version', 'version status', 'networkZone', 'networkAddresses', 'loadBalancerAddresses', 'type', 'environments', 'autoUpdateSettings', 'enabledModules')
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


def get_cluster_version(env, token):
    endpoint = '/api/v1/config/clusterversion'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    entities_json = r.json()
    version = entities_json.get('version')
    return version


def get_active_gate_auto_update_setting(env, token):
    endpoint = '/api/v2/settings/objects'
    schema_ids = 'builtin:deployment.activegate.updates'
    schema_ids_param = f'schemaIds={schema_ids}'
    raw_params = schema_ids_param + '&scopes=environment&fields=schemaId,value,Summary'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token, params=params)
    # active_gate_auto_update_setting = r.json()
    active_gate_auto_update_setting = r.json().get('items')[0].get('value').get('autoUpdate')
    return active_gate_auto_update_setting


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
    # print(summarize(env, token))


if __name__ == '__main__':
    main()
