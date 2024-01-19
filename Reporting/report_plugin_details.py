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

    endpoint = '/api/config/v1/plugins'
    plugin_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for plugin_json in plugin_json_list:
        inner_plugin_json_list = plugin_json.get('values')
        for inner_plugin_json in inner_plugin_json_list:
            entity_id = inner_plugin_json.get('id')
            name = inner_plugin_json.get('name')
            description = inner_plugin_json.get('description')

            if not summary_mode:
                rows.append((entity_id, name, description))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' plugins currently uploaded.')

    if not summary_mode:
        report_name = 'Plugins'
        report_writer.initialize_text_file(None)
        report_headers = ('id', 'name', 'description')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Plugins: ' + str(count_total)])
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
