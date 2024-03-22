import os
import requests

from Reuse import environment
from Reuse import report_writer

# First, try to get the new/improved names
account_id = os.getenv('DYNATRACE_AUTOMATION_ACCOUNT_ID')
client_id = os.getenv('DYNATRACE_AUTOMATION_CLIENT_ID')
client_secret = os.getenv('DYNATRACE_AUTOMATION_CLIENT_SECRET')
skip_slow_api_calls = environment.get_boolean_environment_variable('SKIP_SLOW_API_CALLS', 'True')
environment_variable_source = 'Environment Variable Names'


configuration_path = 'configurations.yaml'
if os.path.isfile(configuration_path):
    account_id = environment.get_configuration('account_id', configuration_file=configuration_path)
    client_id = environment.get_configuration('client_id', configuration_file=configuration_path)
    client_secret = environment.get_configuration('client_secret', configuration_file=configuration_path)
    skip_slow_api_calls = environment.get_configuration('skip_slow_api_calls', configuration_file=configuration_path)
    environment_variable_source = 'Configuration File'

print('Masked environment variables:')
print(f'account_id: {account_id[:10]}*')
print(f'client_secret: {client_secret[:5]}*{client_secret[70:]}')
print(f'client_id: {client_id[:10]}*')
print(f'skip_slow_api_calls: {skip_slow_api_calls}')
print(f'environment_variable_source: {environment_variable_source}')


def get_users():
    r = get_account_management_api('users')
    return r.json()


def get_account_management_api(api_type):
    oauth_bearer_token = get_oauth_bearer_token()
    url = f'https://api.dynatrace.com/iam/v1/accounts/{account_id}/{api_type}'
    if api_type in ['environments', 'subscriptions']:
        url = f'https://api.dynatrace.com/env/v1/accounts/{account_id}/{api_type}'
    if api_type in ['time-zones', 'regions']:
        url = f'https://api.dynatrace.com/ref/v1/{api_type}'
    if api_type == 'permissions':
        url = 'https://api.dynatrace.com/ref/v1/account/permissions'

    headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        # print(r.text)
        return r
    else:
        print(f'GET Request to Account Management API {api_type} Endpoint Failed:')
        print(f'Response Status Code: {r.status_code}')
        print(f'Response Reason:      {r.reason}')
        print(f'Response Text:        {r.text}')
        print("Exiting Program")
        exit(1)


def get_oauth_bearer_token():
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    r = requests.post(f'https://sso.dynatrace.com/sso/oauth2/token?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}&scope=account-idm-read account-idm-write&resource=urn:dtaccount:{account_id}', headers=headers)
    if r.status_code == 200:
        oauth_bearer_token = r.json()["access_token"]
        return oauth_bearer_token
    else:
        print(f'POST Request to Get OAuth Bearer Token Failed:')
        print(f'Response Status Code: {r.status_code}')
        print(f'Response Reason:      {r.reason}')
        print(f'Response Text:        {r.text}')
        print("Exiting Program")
        exit(1)


def report_users():
    users_object = get_users()
    users = users_object.get('items')
    headers = ('User ID', 'Email', 'Name')
    rows = []
    for user in users:
        print(user)
        # user_uid = user.get('uid')
        user_email = user.get('email')
        user_name = user.get('name')
        user_surname = user.get('surname')
        # user_emergency_contact = user.get('emergencyContact')
        # user_status = user.get('userStatus')
        # user_login_metadata = user.get('userLoginMetadata')
        # if user_login_metadata:
        #     user_successful_login_counter = user_login_metadata.get('successfulLoginCounter')
        #     user_failed_login_counter = user_login_metadata.get('failedLoginCounter')
        #     user_last_successful_login = user_login_metadata.get('lastSuccessfulLogin')
        #     user_last_failed_login = user_login_metadata.get('lastFailedLogin')
        #     user_reset_password_token_sent_at = user_login_metadata.get('resetPasswordTokenSentAt')
        #     user_last_successful_basic_authentication = user_login_metadata.get('lastSuccessfulBasicAuthentication')
        #     user_created_at = user_login_metadata.get('createdAt')
        #     user_updated_at = user_login_metadata.get('updatedAt')
        rows.append((user_email, user_name, user_surname))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def append_report(report_name, headers, rows, tuple_lists):
    console_tuple_list, worksheet_tuple_list, html_tuple_list = tuple_lists
    console_tuple_list.append((report_name, headers, rows, '|'))
    worksheet_tuple_list.append((report_name, headers, rows, None, None))
    html_tuple_list.append((report_name, headers, rows))


def process():
    console_tuple_list = []
    worksheet_tuple_list = []
    html_tuple_list = []
    tuple_lists = [console_tuple_list, worksheet_tuple_list, html_tuple_list]

    headers, rows = report_users()
    append_report('Users', headers, rows, tuple_lists)

    # Write Reports
    report_writer.initialize_text_file(None)
    report_writer.write_console_group(console_tuple_list)
    report_writer.write_text_group(None, console_tuple_list)
    report_writer.write_xlsx_worksheets(None, worksheet_tuple_list)
    report_writer.write_html_group(None, html_tuple_list)


if __name__ == '__main__':
    process()
