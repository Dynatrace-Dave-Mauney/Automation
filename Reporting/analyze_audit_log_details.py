# https://www.dynatrace.com/support/help/shortlink/api-audit-logs-get-log-entry

import re
from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    timeframe = 'now-30d'
    # timeframe = 'now-5d'
    # timeframe = 'now-1h'

    rows = []
    summary = []

    count_total = 0

    counts_event_type = {}

    combo_list = []

    endpoint = '/api/v2/auditlogs'
    params = 'pageSize=5000&from=' + timeframe
    auditlog_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for auditlog_json in auditlog_json_list:
        inner_auditlog_json_list = auditlog_json.get('auditLogs')
        for inner_auditlog_json in inner_auditlog_json_list:

            event_type = inner_auditlog_json.get('eventType')
            category = inner_auditlog_json.get('category')
            entity_id = inner_auditlog_json.get('entityId')
            patch = inner_auditlog_json.get('patch', '')

            if event_type == 'CREATE' or event_type == 'UPDATE':
                entity_cleaned = entity_id.split()[0].replace(':', '')
                entity_cleaned = re.sub('dt0c01.+', 'dt0c01.<masked>', entity_cleaned)
                combo = category + '|' + entity_cleaned
                if combo not in combo_list:
                    combo_list.append(combo)

                if not summary_mode:
                    rows.append((event_type, category, entity_id, str(patch)))

            count_total += 1

            counts_event_type[event_type] = counts_event_type.get(event_type, 0) + 1

    timeframe_string = timeframe.replace('now-', '-')
    timeframe_string = timeframe_string.replace('m', ' minutes')
    timeframe_string = timeframe_string.replace('h', ' hours')
    timeframe_string = timeframe_string.replace('d', ' days')
    timeframe_string = timeframe_string.replace('w', ' weeks')
    timeframe_string = timeframe_string.replace('M', ' months')
    timeframe_string = timeframe_string.replace('-', 'for the last ')

    counts_event_type_str = sort_and_stringify_dictionary_items(counts_event_type)

    summary.append('There are ' + str(count_total) + ' audit log entries ' + timeframe_string + '.')
    if count_total > 0:
        summary.append('The entity type breakdown is ' + counts_event_type_str)

    summary.append('')
    summary.append('Unique category and entity ID combinations for CREATE and UPDATE event types: ')

    combo_list.sort()
    for combo in combo_list:
        summary.append(combo)

    if not summary_mode:
        report_name = 'Audit Logs'
        report_headers = ('eventType', 'category', 'entityId', 'patch')
        report_writer.initialize_text_file(None)
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total audit log entries: ' + str(count_total) + ' (' + timeframe_string + ')'])
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
