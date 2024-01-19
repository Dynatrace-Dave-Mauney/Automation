from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []

    count_total = 0
    count_custom = 0

    endpoint = '/api/config/v1/extensions'
    params = 'pageSize=500'
    extension_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for extension_json in extension_json_list:
        inner_extension_json_list = extension_json.get('extensions')
        for inner_extension_json in inner_extension_json_list:
            entity_id = inner_extension_json.get('id')
            name = inner_extension_json.get('name')
            entity_type = inner_extension_json.get('type')

            if entity_id == 'custom.python.ad_replication_checks':
                r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}/global', token)
                extension = r.json()
                properties = extension.get('properties')
                share_hosts = properties.get('share_hosts')
                share_hosts_split = share_hosts.split(',')
                for share_host in sorted(share_hosts_split):
                    if not summary_mode:
                        rows.append((entity_id, name, entity_type, share_host))

            if not summary_mode:
                rows.append((entity_id, name, entity_type, ''))

            count_total += 1
            if not entity_id.startswith('dynatrace'):
                count_custom += 1

    summary.append('There are ' + str(count_total) + ' extensions available. ' + 'There are ' + str(count_custom) + ' custom extensions currently available.')

    if not summary_mode:
        report_name = 'Extensions'
        report_writer.initialize_text_file(None)
        report_headers = ('Entity ID', 'Name', 'Entity Type', 'Comment')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Extensions: ' + str(count_total)])
        write_strings(['Total Custom Extensions: ' + str(count_custom)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
