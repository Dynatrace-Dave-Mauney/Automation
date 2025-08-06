# Report on various tagged entities with an emphasis on finding tags that are key-only rather than key/value pairs.

import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


state_counts = {}

def process(env, token):
    return process_report(env, token)


def process_report(env, token):
    state_skip_list = [
        'ok',
        'process_group_disabled_via_injection_rule',
        'agent_injection_suppression',
        'deep_monitoring_successful',
    ]

    rows = []

    endpoint = '/api/v2/monitoringstate'
    
    raw_params = f'entitySelector=type(PROCESS_GROUP_INSTANCE)'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    monitored_entities_state_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    # print(monitored_entities_state_json_list)

    for monitored_entities_state_json in monitored_entities_state_json_list:
        print(monitored_entities_state_json)
        inner_monitored_entities_state_json_list = monitored_entities_state_json.get('monitoringStates')
        for inner_monitored_entities_state_json in inner_monitored_entities_state_json_list:
            # print(monitored_entities_state_json)
            entity_id = inner_monitored_entities_state_json.get('entityId', '')
            state = inner_monitored_entities_state_json.get('state', '')
            if state not in state_skip_list:
                rows.append((entity_id, state))
            count_state(state)

    rows.append(('', ''))
    for key in sorted(state_counts.keys()):
        rows.append((key, state_counts[key]))

    report_name = 'Monitoring State'
    report_writer.initialize_text_file(None)
    report_headers = ('Entity ID', 'State')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def count_state(state):
    global state_counts
    try:
        current = state_counts[state]
        state_counts[state] = current + 1
    except KeyError:
        state_counts[state] = 1

    try:
        current = state_counts['TOTAL']
        state_counts['TOTAL'] = current + 1
    except KeyError:
        state_counts['TOTAL'] = 1


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
