from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def load_management_zone_dict(env, token):
    management_zone_dict = {}
    endpoint = '/api/config/v1/managementZones'
    management_zones_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        for inner_management_zones_json in inner_management_zones_json_list:
            name = inner_management_zones_json.get('name')
            if name.endswith('-PROD') or name.endswith('-PRD') or name.endswith('-DR'):
                management_zone_id = inner_management_zones_json.get('id')
                management_zone_dict[management_zone_id] = name

    return management_zone_dict


def process(env, token):
    return process_report(env, token)


def process_report(env, token):
    management_zone_dict = load_management_zone_dict(env, token)

    rows = []

    count_total = 0

    endpoint = '/api/config/v1/alertingProfiles'
    alerting_profiles_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    for alerting_profiles_json in alerting_profiles_json_list:
        inner_alerting_profiles_json_list = alerting_profiles_json.get('values')
        for inner_alerting_profiles_json in inner_alerting_profiles_json_list:
            entity_id = inner_alerting_profiles_json.get('id')
            name = inner_alerting_profiles_json.get('name')

            endpoint = '/api/config/v1/alertingProfiles/' + entity_id
            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
            alerting_profile = r.json()

            management_zone_id = alerting_profile.get('managementZoneId')

            management_zone_name = management_zone_dict.get(str(management_zone_id), None)

            if not management_zone_name:
                rows.append((name, entity_id, str(management_zone_id)))

            count_total += 1

    rows = sorted(rows)
    report_name = 'Alerting Profiles with bad MZs'
    report_writer.initialize_text_file(None)
    report_headers = ('Name', 'ID', 'Management Zone ID')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    write_strings(['Total alerting_profiles: ' + str(count_total)])
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


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
