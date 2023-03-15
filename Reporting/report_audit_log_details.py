# https://www.dynatrace.com/support/help/shortlink/api-audit-logs-get-log-entry

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    # timeframe = 'now-30d'
    # timeframe = 'now-5d'
    timeframe = 'now-24h'
    # timeframe = 'now-1h'
    summary = []

    count_total = 0

    counts_event_type = {}

    endpoint = '/api/v2/auditlogs'
    params = 'pageSize=5000&from=' + timeframe
    auditlog_json_list = dynatrace_api.get(env, token, endpoint, params)

    # print(auditlog_json_list)
    # exit()

    if print_mode:
        print('log' + '|' + 'eventType' + '|' + 'category' + '|' + 'entityId' + '|' + 'environmentId' + '|' + 'user' + '|' + 'userType' + '|' + 'userOrigin' + '|' + 'timestamp' + '|' + 'success' + '|' + 'patch')

    for auditlog_json in auditlog_json_list:
        inner_auditlog_json_list = auditlog_json.get('auditLogs')
        for inner_auditlog_json in inner_auditlog_json_list:
            # print(inner_auditlog_json)

            log_id = inner_auditlog_json.get('logId')
            event_type = inner_auditlog_json.get('eventType')
            category = inner_auditlog_json.get('category')
            entity_id = inner_auditlog_json.get('entityId')
            environment_id = inner_auditlog_json.get('environmentId')
            user = inner_auditlog_json.get('user')
            user_type = inner_auditlog_json.get('userType')
            user_origin = inner_auditlog_json.get('userOrigin')
            timestamp = inner_auditlog_json.get('timestamp')
            success = inner_auditlog_json.get('success')
            patch = inner_auditlog_json.get('patch', '')

            if print_mode:
                print(str(log_id) + '|' + event_type + '|' + category + '|' + entity_id + '|' + environment_id + '|' + user + '|' + user_type + '|' + user_origin + '|' + str(timestamp) + '|' + str(success) + '|' + str(patch))

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
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
