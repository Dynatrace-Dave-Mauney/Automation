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

    endpoint = '/api/config/v1/dataPrivacy'
    params = ''
    data_privacy_json = dynatrace_api.get(env, token, endpoint, params)[0]

    mask_ip_addresses_and_gps_coordinates = data_privacy_json.get('maskIpAddressesAndGpsCoordinates')
    mask_user_action_names = data_privacy_json.get('maskUserActionNames')
    mask_personal_data_in_uris = data_privacy_json.get('maskPersonalDataInUris')
    log_audit_events = data_privacy_json.get('logAuditEvents')

    # TESTING
    # mask_ip_addresses_and_gps_coordinates = True
    # mask_user_action_names = True
    # mask_personal_data_in_uris = True
    # log_audit_events = False

    if not summary_mode:
        rows.append((str(mask_ip_addresses_and_gps_coordinates), str(mask_user_action_names), str(mask_personal_data_in_uris), str(log_audit_events)))

    if not mask_ip_addresses_and_gps_coordinates and not mask_user_action_names and not mask_personal_data_in_uris and log_audit_events:
        summary.append('Data privacy settings reflect the recommended best practice of not masking IP addresses, user action names or personal data in URIs, and of logging audit events.')
    else:
        summary.append('Data privacy settings do not reflect the recommended best practice of not masking IP addresses, user action names or personal data in URIs, and of logging audit events.' + '\r\n' +
                       'Masking of IP addresses is ' + convert_boolean(mask_ip_addresses_and_gps_coordinates) + ', masking of user actions is ' + convert_boolean(mask_user_action_names) + ' and masking of personal data in URIs is ' + convert_boolean(mask_personal_data_in_uris) + '.  Logging of audit events is ' + convert_boolean(log_audit_events) + '.')

    if not summary_mode:
        report_name = 'Data Privacy'
        report_writer.initialize_text_file(None)
        report_headers = ('maskIpAddressesAndGpsCoordinates', 'maskUserActionNames', 'maskPersonalDataInUris', 'logAuditEvents')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def convert_boolean(boolean):
    if boolean:
        return 'on'
    else:
        return'off'


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
