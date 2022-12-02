# https://www.dynatrace.com/support/help/shortlink/api-audit-logs-get-log-entry

import dynatrace_rest_api_helper
import os
import re


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    timeframe = 'now-30d'
    # timeframe = 'now-5d'
    # timeframe = 'now-1h'

    summary = []

    count_total = 0

    counts_event_type = {}

    combo_list = []

    endpoint = '/api/v2/auditlogs'
    params = 'pageSize=5000&from=' + timeframe
    auditlog_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)

    if print_mode:
        print('eventType' + '|' + 'category' + '|' + 'entityId' + '|' + 'patch')

    for auditlog_json in auditlog_json_list:
        # print(auditlog_json)
        inner_auditlog_json_list = auditlog_json.get('auditLogs')
        for inner_auditlog_json in inner_auditlog_json_list:
            # print(inner_auditlog_json)

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

                if print_mode:
                    print(event_type + '|' + category + '|' + entity_id + '|' + str(patch))

            count_total += 1

            counts_event_type[event_type] = counts_event_type.get(event_type, 0) + 1

    timeframe_string = timeframe.replace('now-', '-')
    timeframe_string = timeframe_string.replace('m', ' minutes')
    timeframe_string = timeframe_string.replace('h', ' hours')
    timeframe_string = timeframe_string.replace('d', ' days')
    timeframe_string = timeframe_string.replace('w', ' weeks')
    timeframe_string = timeframe_string.replace('M', ' months')
    timeframe_string = timeframe_string.replace('-', 'for the last ')

    if print_mode:
        print('Total audit log entries: ' + str(count_total) + ' (' + timeframe_string + ')')

    counts_event_type_str = sort_and_stringify_dictionary_items(counts_event_type)

    summary.append('There are ' + str(count_total) + ' audit log entries ' + timeframe_string + '.')
    summary.append('The entity type breakdown is ' + counts_event_type_str)

    summary.append('')
    summary.append('Unique category and entity ID combinations for CREATE and UPDATE event types: ')

    combo_list.sort()
    for combo in combo_list:
        summary.append(combo)

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        # line = line.replace('are 0', 'are no')
        print(line)


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
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'
    print('Audit Log Analysis')
    process(env, token, True)
    # print_list(report_audit_log_details.summarize(env, token))
    # print('')


if __name__ == '__main__':
    main()
