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

    endpoint = '/api/v1/oneagents'
    params = 'activeGateId=DIRECT_COMMUNICATION&relativeTime=2hours'
    oneagents_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for oneagents_json in oneagents_json_list:
        inner_oneagents_json_list = oneagents_json.get('hosts')
        for inner_oneagents_json in inner_oneagents_json_list:
            host_info = inner_oneagents_json.get('hostInfo')
            entity_id = host_info.get('entityId')
            display_name = host_info.get('displayName')
            discovered_name = host_info.get('discoveredName')

            if not summary_mode:
                rows.append((str(display_name), str(discovered_name), str(entity_id)))

            count_total += 1

    if not summary_mode:
        print('Total oneagents in direct communication with the Dynatrace cluster: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' oneagents in direct communication with the Dynatrace cluster.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'OneAgent Direct Communication'
        report_writer.initialize_text_file(None)
        report_headers = ('displayName', 'discoveredName', 'entityId')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total OneAgents in direct communication with the Dynatrace cluster: ' + str(count_total)])
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
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    # print(summarize(env, token))

    
if __name__ == '__main__':
    main()
