import urllib.parse

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

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(APPLICATION)&fields=+properties&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            properties = inner_entities_json.get('properties')
            detected_name = properties.get('detectedName', '')
            application_type = properties.get('applicationType', '')
            application_injection_type = properties.get('applicationInjectionType', '')
            rule_applied_match_type = properties.get('ruleAppliedMatchType', '')
            application_match_target = properties.get('applicationMatchTarget', '')
            rule_applied_pattern = properties.get('ruleAppliedPattern', '')
            customized_name = properties.get('customizedName', '')

            if not summary_mode:
                rows.append((display_name, customized_name, detected_name, entity_id, application_type, application_injection_type, rule_applied_match_type, application_match_target, rule_applied_pattern))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' web applications currently defined and reporting data.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Applications'
        report_writer.initialize_text_file(None)
        report_headers = ('displayName', 'customizedName', 'detectedName', 'entityId', 'applicationType', 'applicationInjectionType', 'ruleAppliedMatchType', 'applicationMatchTarget', 'ruleAppliedPattern')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total applications: ' + str(count_total)])
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
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
