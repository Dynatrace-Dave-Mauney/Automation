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

    endpoint = '/api/v2/eventTypes'
    events_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for events_json in events_json_list:
        inner_events_json_list = events_json.get('eventTypeInfos')
        for inner_events_json in inner_events_json_list:
            event_type = inner_events_json.get('type')
            display_name = inner_events_json.get('displayName')
            if not summary_mode:
                rows.append((event_type, display_name))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' events currently defined.')

    if not summary_mode:
        report_name = 'Events'
        report_writer.initialize_text_file(None)
        report_headers = ('Type', 'Display Name')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Events: ' + str(count_total)])
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
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
