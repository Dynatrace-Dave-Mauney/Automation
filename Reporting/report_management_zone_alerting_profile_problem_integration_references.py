from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []

    management_zone_dict = load_management_zone_dict(env, token)
    # print(management_zone_dict)

    alerting_profile_references_dict = load_and_count_alerting_profile_references(env, token, management_zone_dict)
    # print(management_zone_dict)

    count_problem_notification_references(env, token, management_zone_dict, alerting_profile_references_dict)
    # print(management_zone_dict)

    keys = management_zone_dict.keys()
    for key in keys:
        child_dict = management_zone_dict[key]
        management_zone_name = child_dict.get('name')
        alerting_profile_references = child_dict.get('AlertRefs')
        problem_notification_email_references = child_dict.get('NotifyEmailRefs')
        problem_notification_pager_duty_references = child_dict.get('NotifyPagerDutyRefs')
        problem_notification_other_references = child_dict.get('NotifyOtherRefs')
        rows.append((management_zone_name, alerting_profile_references, problem_notification_pager_duty_references, problem_notification_email_references, problem_notification_other_references))

    rows = sorted(rows)
    report_name = 'MZ-AP-PN Cross-Reference'
    report_writer.initialize_text_file(None)
    report_headers = ('Management Zone', 'Alerting Profile References', 'Problem Notification Pager Duty References', 'Problem Notification Email References', 'Problem Notification Other References')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


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
                management_zone_dict[management_zone_id] = {'name': name, 'AlertRefs': 0, 'NotifyEmailRefs': 0, 'NotifyPagerDutyRefs': 0, 'NotifyOtherRefs': 0}

    return management_zone_dict


def load_and_count_alerting_profile_references(env, token, management_zone_dict):
    alerting_profile_references_dict = {}

    endpoint = '/api/config/v1/alertingProfiles'
    alerting_profiles_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for alerting_profiles_json in alerting_profiles_json_list:
        inner_alerting_profiles_json_list = alerting_profiles_json.get('values')
        for inner_alerting_profiles_json in inner_alerting_profiles_json_list:
            # print(inner_alerting_profiles_json)
            name = inner_alerting_profiles_json.get('name')
            entity_id = inner_alerting_profiles_json.get('id')
            endpoint = '/api/config/v1/alertingProfiles/' + entity_id
            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
            alerting_profile = r.json()
            management_zone_id = alerting_profile.get('managementZoneId')
            # print(management_zone_id)
            management_zone_counts = management_zone_dict.get(str(management_zone_id), None)
            if management_zone_counts:
                # print(name, management_zone_id, management_zone_counts)
                management_zone_counts['AlertRefs'] = management_zone_counts.get('AlertRefs') + 1
                management_zone_dict[str(management_zone_id)] = management_zone_counts
                alerting_profile_references_dict[entity_id] = management_zone_id
            else:
                pass
                # print(name, management_zone_id, 'No management_zone_counts for alerting profile "managementZoneId"')

    return alerting_profile_references_dict


def count_problem_notification_references(env, token, management_zone_dict, alerting_profile_references_dict):
    endpoint = '/api/config/v1/notifications'
    notifications_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    for notifications_json in notifications_json_list:
        inner_notifications_json_list = notifications_json.get('values')
        for inner_notifications_json in inner_notifications_json_list:
            # print(inner_notifications_json)
            entity_id = inner_notifications_json.get('id')
            name = inner_notifications_json.get('name')
            endpoint = '/api/config/v1/notifications'
            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            notification = r.json()
            alerting_profile = notification.get('alertingProfile')
            notification_type = notification.get('type')

            notification_reference_type = 'NotifyOtherRefs'
            if notification_type == 'PAGER_DUTY':
                notification_reference_type = 'NotifyPagerDutyRefs'
            else:
                if notification_type == 'WEBHOOK':
                    url = notification.get('url')
                    if url and 'pagerduty' in url:
                        notification_reference_type = 'NotifyPagerDutyRefs'
                else:
                    if notification_type == 'EMAIL':
                        notification_reference_type = 'NotifyEmailRefs'

            management_zone_id = alerting_profile_references_dict.get(alerting_profile, None)
            # print(name, notification_reference_type, alerting_profile, management_zone_id)
            if management_zone_id:
                management_zone_counts = management_zone_dict.get(str(management_zone_id), None)
                # print(management_zone_counts)
                if management_zone_counts:
                    # print(name, management_zone_id, management_zone_counts)
                    management_zone_counts[notification_reference_type] = management_zone_counts.get(notification_reference_type) + 1
                    management_zone_dict[str(management_zone_id)] = management_zone_counts
                else:
                    pass
                    # print(name, management_zone_id, 'No management_zone_counts')
            else:
                pass
                # print(name, management_zone_id, 'No management_zone_id')


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
