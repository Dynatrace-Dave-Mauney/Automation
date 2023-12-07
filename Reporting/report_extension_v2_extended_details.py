from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []

    count_total = 0

    endpoint = '/api/v2/extensions'
    params = 'pageSize=100'
    extension_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for extension_json in extension_json_list:
        inner_extension_json_list = extension_json.get('extensions')
        for inner_extension_json in inner_extension_json_list:
            # print(inner_extension_json)
            extension_name = inner_extension_json.get('extensionName')
            extension_version = inner_extension_json.get('version')

            endpoint = f'/api/v2/extensions/{extension_name}/monitoringConfigurations'
            extension_configuration_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
            for extension_configuration_json in extension_configuration_json_list:
                inner_extension_configuration_json_list = extension_configuration_json.get('items')
                for inner_extension_configuration_json in inner_extension_configuration_json_list:
                    # print(inner_extension_configuration_json)
                    extension_remote_keys = {'com.dynatrace.extension.sql-oracle': 'sqlOracleRemote', 'com.dynatrace.extension.sql-server': 'sqlServerRemote'}
                    if extension_name in extension_remote_keys.keys():
                        extension_remote_key = extension_remote_keys.get(extension_name)
                        extension_value = inner_extension_configuration_json.get('value')
                        # print(extension_value)
                        extension_remote = extension_value.get(extension_remote_key)
                        # print(extension_remote)
                        extension_endpoints = extension_remote.get('endpoints')
                        # print(extension_endpoints)
                        for extension_endpoint in extension_endpoints:
                            extension_host = extension_endpoint.get('host')
                            extension_port = extension_endpoint.get('port')
                            rows.append((extension_name, extension_version, extension_host, extension_port, ''))
                    else:
                        msg = f'Cannot go deeper for {extension_name} until specific logic is added!'
                        print(msg)
                        rows.append((extension_name, extension_version, 'N/A', 'NA', msg))
                        continue

            count_total += 1

    report_name = 'Extensions 2.0 (Extended)'
    report_writer.initialize_text_file(None)
    report_headers = (['Extension Name', 'Extension Version', 'Endpoint Host', 'Endpoint Port', 'Comment'])
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    write_strings(['Total Extensions 2.0: ' + str(count_total)])
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


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
