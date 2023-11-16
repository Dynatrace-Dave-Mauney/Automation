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

    endpoint = '/api/config/v1/alertingProfiles'
    params = ''
    alerting_profiles_json_list = dynatrace_api.get(env, token, endpoint, params)

    for alerting_profiles_json in alerting_profiles_json_list:
        inner_alerting_profiles_json_list = alerting_profiles_json.get('values')
        for inner_alerting_profiles_json in inner_alerting_profiles_json_list:
            entity_id = inner_alerting_profiles_json.get('id')
            name = inner_alerting_profiles_json.get('name')

            # if '-PRD' not in name.upper():
            #     continue

            endpoint = '/api/config/v1/alertingProfiles/' + entity_id
            params = ''
            alerting_profile = dynatrace_api.get(env, token, endpoint, params)[0]  # No pagination needed

            if not summary_mode:
                management_zone_id = alerting_profile.get('managementZoneId')
                event_type_filters = alerting_profile.get('eventTypeFilters')
                formatted_rules = format_rules(alerting_profile.get('rules'))
                if event_type_filters:
                    rows.append((name, entity_id, str(management_zone_id), formatted_rules, str(event_type_filters)))
                else:
                    rows.append((name, entity_id, str(management_zone_id), formatted_rules))
            count_total += 1

    summary.append('There are ' + str(count_total) + ' alerting profiles currently defined.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Alerting Profiles'
        report_writer.initialize_text_file(None)
        report_headers = ('name', 'id', 'managementZoneId', 'rules', 'eventTypeFilters')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total alerting_profiles: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def format_rules(rules):
    formatted_rules = []
    for rule in rules:
        severity_level = rule.get('severityLevel')
        delay_in_minutes = rule.get('delayInMinutes')
        tag_filter = rule.get('tagFilter')
        tag_filters = tag_filter.get('tagFilters')
        if not tag_filters:
            formatted_rules.append(f'{severity_level}: {delay_in_minutes}')
        else:
            formatted_rules.append(f'{severity_level}: {delay_in_minutes}: {str(tag_filters)}')

    return str(formatted_rules)


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
