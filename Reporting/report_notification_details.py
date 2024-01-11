from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer
from Reuse import standards


perform_check_naming_standard = False
report_naming_standard_violations_only = False
configuration_object = environment.get_configuration_object('configurations.yaml')


def summarize(env, token, **kwargs):
    global perform_check_naming_standard
    if kwargs:
        perform_check_naming_standard = kwargs.get('perform_check_naming_standard', False)
    return process_report(env, token, True, **kwargs)


def process(env, token, **kwargs):
    global perform_check_naming_standard
    global report_naming_standard_violations_only
    if kwargs:
        perform_check_naming_standard = kwargs.get('perform_check_naming_standard', False)
        report_naming_standard_violations_only = kwargs.get('report_naming_standard_violations_only', False)
    return process_report(env, token, False, **kwargs)


def process_report(env, token, summary_mode, **kwargs):
    rows = []
    summary = []

    count_total = 0
    count_naming_standard_pass = 0
    count_naming_standard_fail = 0

    endpoint = '/api/config/v1/notifications'
    notifications_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for notifications_json in notifications_json_list:
        inner_notifications_json_list = notifications_json.get('values')
        for inner_notifications_json in inner_notifications_json_list:
            entity_id = inner_notifications_json.get('id')
            name = inner_notifications_json.get('name')

            # if '-PRD' not in name.upper():
            #     continue

            endpoint = '/api/config/v1/notifications'
            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            notification = r.json()

            # print(notification)
            notification_type = notification.get('type')
            alerting_profile = notification.get('alertingProfile')
            active = notification.get('active')
            url = notification.get('url')
            accept_any_certificate = notification.get('acceptAnyCertificate')
            # payload = notification.get('payload')
            payload = 'skipped for performance'
            subject = notification.get('subject')
            body = notification.get('body')
            receivers = notification.get('receivers')
            if not receivers:
                receivers = ''
            else:
                if len(receivers) == 1:
                    receivers = receivers[0]
            cc_receivers = notification.get('ccReceivers')
            if not cc_receivers:
                cc_receivers = ''
            bcc_receivers = notification.get('bccReceivers')
            if not bcc_receivers:
                bcc_receivers = ''

            standard_string = 'N/A'
            if perform_check_naming_standard:
                standard_met, reason = check_naming_standard(name, **kwargs)
                if standard_met:
                    standard_string = 'Meets naming standards'
                    count_naming_standard_pass += 1
                else:
                    standard_string = f'Does not meet naming standards because {reason}'
                    # print(name, standard_string)
                    count_naming_standard_fail += 1

            if not summary_mode:
                rows.append((name, standard_string, entity_id, notification_type, alerting_profile, active, url, accept_any_certificate, payload, subject, body, str(receivers), str(cc_receivers), str(bcc_receivers)))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' notifications currently defined.')

    if count_total > 0 and perform_check_naming_standard:
        summary.append(f'There are {count_naming_standard_pass} notifications currently defined that meet the naming standard.')
        summary.append(f'There are {count_naming_standard_fail} notifications currently defined that do not meet the naming standard.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Notifications'
        report_writer.initialize_text_file(None)
        report_headers = ('Name', '', 'Naming Standard Finding', 'ID', 'Notification Type', 'Alerting Profile', 'Active', 'URL', 'Accept Any Certificate', 'Payload', 'Subject', 'Body', 'Receivers', 'CC Receivers', 'BCC Receivers')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Notifications: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def check_naming_standard(name, **kwargs):
    env_name = kwargs.get('env_name')
    if not env_name:
        return False, 'Environment name ("env_name") must be passed'

    if not configuration_object:
        return False, 'Configuration object ("configuration_object") could not be loaded'

    return standards.check_naming_standard(env_name, name, configuration_object, 'notification')


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
    # process(env, token)
    process(env, token, env_name=env_name_supplied, perform_check_naming_standard=True)
    # print(summarize(env, token, env_name=env_name_supplied, perform_check_naming_standard=True))
    
    
if __name__ == '__main__':
    main()
