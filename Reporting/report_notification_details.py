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

    endpoint = '/api/config/v1/notifications'
    params = ''
    notifications_json_list = dynatrace_api.get(env, token, endpoint, params)

    for notifications_json in notifications_json_list:
        inner_notifications_json_list = notifications_json.get('values')
        for inner_notifications_json in inner_notifications_json_list:
            entity_id = inner_notifications_json.get('id')
            name = inner_notifications_json.get('name')
            endpoint = '/api/config/v1/notifications/' + entity_id
            params = ''
            notification = dynatrace_api.get(env, token, endpoint, params)[0]
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

            if not summary_mode:
                rows.append((entity_id, name, notification_type, alerting_profile, active, url, accept_any_certificate, payload, subject, body, str(receivers), str(cc_receivers), str(bcc_receivers)))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' notifications currently defined.')

    if not summary_mode:
        report_name = 'Notifications'
        report_writer.initialize_text_file(None)
        report_headers = ('id', 'name', 'notificationType', 'alertingProfile', 'active', 'url', 'acceptAnyCertificate', 'payload', 'subject', 'body', 'receivers', 'ccReceivers', 'bccReceivers')
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
