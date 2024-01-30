# Report audit log details
# https://www.dynatrace.com/support/help/shortlink/api-audit-logs-get-log-entry

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    timeframe = 'now-30d'
    # timeframe = 'now-5d'
    # timeframe = 'now-24h'
    # timeframe = 'now-1h'
    summary = []

    count_total = 0

    counts_event_type = {}

    endpoint = '/api/v2/auditlogs'
    params = 'pageSize=5000&from=' + timeframe
    auditlog_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for auditlog_json in auditlog_json_list:
        inner_auditlog_json_list = auditlog_json.get('auditLogs')
        for inner_auditlog_json in inner_auditlog_json_list:
            log_id = inner_auditlog_json.get('logId')
            event_type = inner_auditlog_json.get('eventType')

            # Usually we want to ignore logins and logouts
            # if 'LOGIN' in event_type or 'LOGOUT' in event_type:
            #    continue

            category = inner_auditlog_json.get('category')
            entity_id = inner_auditlog_json.get('entityId')
            environment_id = inner_auditlog_json.get('environmentId')
            user = inner_auditlog_json.get('user')
            user_type = inner_auditlog_json.get('userType')
            user_origin = inner_auditlog_json.get('userOrigin')
            timestamp = inner_auditlog_json.get('timestamp')
            success = inner_auditlog_json.get('success')
            patch = inner_auditlog_json.get('patch', '')

            if not summary_mode:
                rows.append((str(log_id), event_type, category, entity_id, environment_id, user, user_type, user_origin, str(timestamp), str(success), str(patch)))

            count_total += 1

            counts_event_type[event_type] = counts_event_type.get(event_type, 0) + 1

    timeframe_string = timeframe.replace('now-', '-')
    timeframe_string = timeframe_string.replace('m', ' minutes')
    timeframe_string = timeframe_string.replace('h', ' hours')
    timeframe_string = timeframe_string.replace('d', ' days')
    timeframe_string = timeframe_string.replace('w', ' weeks')
    timeframe_string = timeframe_string.replace('M', ' months')
    timeframe_string = timeframe_string.replace('-', 'for the last ')

    if not summary_mode:
        print('Total audit log entries: ' + str(count_total) + ' (' + timeframe_string + ')')

    counts_event_type_str = sort_and_stringify_dictionary_items(counts_event_type)

    summary.append('There are ' + str(count_total) + ' audit log entries ' + timeframe_string + '.')
    summary.append('The entity type breakdown is ' + counts_event_type_str)

    if not summary_mode:
        report_name = 'Audit Logs'
        report_writer.initialize_text_file(None)
        report_headers = ('log', 'eventType', 'category', 'entityId', 'environmentId', 'user', 'userType', 'userOrigin', 'timestamp', 'success', 'patch')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Audit Log Entries: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def sort_and_stringify_dictionary_items(any_dict):
    dict_str = str(sorted(any_dict.items()))
    dict_str = dict_str.replace('[', '')
    dict_str = dict_str.replace(']', '')
    dict_str = dict_str.replace('), (', '~COMMA~')
    dict_str = dict_str.replace('(', '')
    dict_str = dict_str.replace(')', '')
    dict_str = dict_str.replace(',', ':')
    dict_str = dict_str.replace('~COMMA~', ', ')
    dict_str = dict_str.replace("'", "")
    return dict_str


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
    
    
if __name__ == '__main__':
    main()
