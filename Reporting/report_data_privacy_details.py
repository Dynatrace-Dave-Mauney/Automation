import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    endpoint = '/api/config/v1/dataPrivacy'
    params = ''
    data_privacy_json = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]

    if print_mode:
        print('maskIpAddressesAndGpsCoordinates' + '|' + 'maskUserActionNames' + '|' + 'maskPersonalDataInUris' + '|' + 'logAuditEvents')

    mask_ip_addresses_and_gps_coordinates = data_privacy_json.get('maskIpAddressesAndGpsCoordinates')
    mask_user_action_names = data_privacy_json.get('maskUserActionNames')
    mask_personal_data_in_uris = data_privacy_json.get('maskPersonalDataInUris')
    log_audit_events = data_privacy_json.get('logAuditEvents')

    # TESTING
    # mask_ip_addresses_and_gps_coordinates = True
    # mask_user_action_names = True
    # mask_personal_data_in_uris = True
    # log_audit_events = False

    if print_mode:
        print(str(mask_ip_addresses_and_gps_coordinates) + '|' + str(mask_user_action_names) + '|' + str(mask_personal_data_in_uris) + '|' + str(log_audit_events))

    if not mask_ip_addresses_and_gps_coordinates and not mask_user_action_names and not mask_personal_data_in_uris and log_audit_events:
        summary.append('Data privacy settings reflect the recommended best practice of not masking IP addresses, user action names or personal data in URIs, and of logging audit events.')
    else:
        summary.append('Data privacy settings do not reflect the recommended best practice of not masking IP addresses, user action names or personal data in URIs, and of logging audit events.' + '\r\n' +
                       'Masking of IP addresses is ' + convert_boolean(mask_ip_addresses_and_gps_coordinates) + ', masking of user actions is ' + convert_boolean(mask_user_action_names) + ' and masking of personal data in URIs is ' + convert_boolean(mask_personal_data_in_uris) + '.  Logging of audit events is ' + convert_boolean(log_audit_events) + '.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def convert_boolean(boolean):
    if boolean:
        return 'on'
    else:
        return'off'


def main():
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, True)


if __name__ == '__main__':
    # print('Not to be run standalone.  Use one of the "perform_*.py" modules to run this module.')
    # exit(1)
    main()
