# import json
import os
import requests

from Reuse import environment
from Reuse import report_writer
# from Reuse import directories_and_files

"""
Reporting for: https://api.dynatrace.com/spec/

Creating an OAuth Client:
Old UI: Person Icon > Account Settings > Pick Account if needed > Identity & access management > OAuth Clients > "Create client" button
New UI: Person Icon > Account Management > Pick Account if needed > Identity & access management > OAuth Clients > "Create client" button
Assign all permissions under the Account section:
account-idm-read, account-idm-write, account-env-read, account-env-write, account-uac-read, account-uac-write,
iam-policies-management, iam:policies:write, iam:policies:read, iam:bindings:write, iam:bindings:read,
iam:effective-permissions:read

Accessing the Account Management API:
Navigate to https://api.dynatrace.com/spec/ or:
Open the User menu and select Account settings (in latest Dynatrace, Account Management).
On the top navigation bar, go to Identity & access management > OAuth clients.
In the upper-right corner of the page, select Account Management API.

To get the Account ID:
Old UI: Person Icon > Account Settings > Pick Account if needed
New UI: Person Icon > Account Settings > Pick Account if needed
AccountID appears as the query parameter in the address URL
"""

# First, try to get the new/improved names
account_id = os.getenv('DYNATRACE_AUTOMATION_ACCOUNT_ID')
client_id = os.getenv('DYNATRACE_AUTOMATION_CLIENT_ID')
client_secret = os.getenv('DYNATRACE_AUTOMATION_CLIENT_SECRET')
skip_slow_api_calls = environment.get_boolean_environment_variable('SKIP_SLOW_API_CALLS', 'True')
environment_variable_source = 'New Environment Variable Names'


# If the new/improved names are not found, fall back to the older names
if not account_id and not client_id and not client_secret:
    print('WARNING: Using deprecated environment variable names')
    account_id = os.getenv('ACCOUNTID')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    skip_slow_api_calls = environment.get_boolean_environment_variable('DYNATRACE_SKIP_SLOW_ACCOUNT_MANAGEMENT_API_CALLS', 'True')
    environment_variable_source = 'Old Environment Variable Names'

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


def get_groups():
    r = get_account_management_api('groups')
    return r.json()


def get_permissions_for_group(group_uuid):
    api_type = f'groups/{group_uuid}/permissions'
    r = get_account_management_api(api_type)
    return r.json()


def get_users_in_group(group_uuid):
    api_type = f'groups/{group_uuid}/users'
    r = get_account_management_api(api_type)
    return r.json()


def get_permissions():
    r = get_account_management_api('permissions')
    return r.json()


def get_users():
    r = get_account_management_api('users')
    return r.json()


def get_environments():
    r = get_account_management_api('environments')
    return r.json()


def get_regions():
    r = get_account_management_api('regions')
    return r.json()


def get_time_zones():
    r = get_account_management_api('time-zones')
    return r.json()


def get_service_users():
    r = get_account_management_api('service-users')
    return r.json()


def get_subscriptions():
    r = get_account_management_api('subscriptions')
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


def report_groups():
    groups_object = get_groups()
    groups = groups_object.get('items')
    headers = ['Group Name', 'Federated Attribute Values', 'UUID', 'Owner', 'Description', 'Hidden', 'Created', 'Updated']
    rows = []
    for group in groups:
        group_uuid = str(group.get('uuid'))
        group_name = str(group.get('name'))
        group_owner = str(group.get('owner'))
        group_description = str(group.get('description'))
        group_federated_attribute_values = str(group.get('federatedAttributeValues'))
        group_hidden = str(group.get('hidden'))
        group_created_at = str(group.get('createdAt'))
        group_updated_at = str(group.get('updatedAt'))
        rows.append((group_name, group_federated_attribute_values, group_uuid, group_owner, group_description, group_hidden, group_created_at, group_updated_at))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def report_permissions_for_groups(only_show_missing_permissions):
    groups_object = get_groups()
    groups = groups_object.get('items')
    sorted_groups = sorted(groups, key=lambda x: x['name'])
    headers = ('Group Name', 'UUID', 'Permission Name', 'Permission Scope', 'Permission Scope Type', 'Permission Created', 'Permission Updated')
    rows = []
    for group in sorted_groups:
        group_uuid = group.get('uuid')
        group_name = group.get('name')
        permissions_object = get_permissions_for_group(group_uuid)
        permissions = permissions_object.get('permissions')
        # Want to report only groups with permissions?  Comment out the section below...
        if not permissions:
            rows.append((group_name, group_uuid, 'No Permissions!'))
        if not only_show_missing_permissions:
            for permission in permissions:
                permission_name = permission.get('permissionName')
                permission_scope = permission.get('scope')
                permission_scope_type = permission.get('scopeType')
                permission_created_at = permission.get('createdAt')
                permission_updated_at = permission.get('updatedAt')
                rows.append((group_name, group_uuid, permission_name, permission_scope, permission_scope_type, permission_created_at, permission_updated_at))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def report_users_in_groups(only_show_missing_users):
    groups_object = get_groups()
    groups = groups_object.get('items')
    sorted_groups = sorted(groups, key=lambda x: x['name'])
    headers = ['Group Name', 'UUID', 'User ID', 'User Email', 'User Name', 'User Surname', 'User Emergency Contact', 'User Status']
    rows = []
    for group in sorted_groups:
        group_uuid = group.get('uuid')
        group_name = group.get('name')
        users_object = get_users_in_group(group_uuid)
        users = users_object.get('items')
        # Want to report only groups with users?  Comment out the section below...
        if not users:
            rows.append((group_name, group_uuid, 'No users!'))
        if not only_show_missing_users:
            for user in users:
                user_id = user.get('uid')
                user_email = user.get('email')
                user_name = user.get('name')
                user_surname = user.get('surname')
                user_emergency_contact = user.get('emergencyContact')
                user_status = user.get('userStatus')
                rows.append((group_name, group_uuid, user_id, user_email, user_name, user_surname, user_emergency_contact, user_status))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def report_users():
    users_object = get_users()
    users = users_object.get('items')
    headers = ('User ID', 'Email', 'Name', 'Surname', 'Emergency Contact', 'Status', 'Successful Login Counter', 'Failed Login Counter', 'Last Successful Login', 'Last Failed Login', 'Reset Password Token Sent', 'Last Successful Basic Authentication', 'Created', 'Updated')
    rows = []
    for user in users:
        user_uid = user.get('uid')
        user_email = user.get('email')
        user_name = user.get('name')
        user_surname = user.get('surname')
        user_emergency_contact = user.get('emergencyContact')
        user_status = user.get('userStatus')
        user_login_metadata = user.get('userLoginMetadata')
        if user_login_metadata:
            user_successful_login_counter = user_login_metadata.get('successfulLoginCounter')
            user_failed_login_counter = user_login_metadata.get('failedLoginCounter')
            user_last_successful_login = user_login_metadata.get('lastSuccessfulLogin')
            user_last_failed_login = user_login_metadata.get('lastFailedLogin')
            user_reset_password_token_sent_at = user_login_metadata.get('resetPasswordTokenSentAt')
            user_last_successful_basic_authentication = user_login_metadata.get('lastSuccessfulBasicAuthentication')
            user_created_at = user_login_metadata.get('createdAt')
            user_updated_at = user_login_metadata.get('updatedAt')
            rows.append((user_uid, user_email, user_name, user_surname, user_emergency_contact, user_status, user_successful_login_counter, user_failed_login_counter, user_last_successful_login, user_last_failed_login, user_reset_password_token_sent_at, user_last_successful_basic_authentication, user_created_at, user_updated_at))
        else:
            rows.append((user_uid, user_email, user_name, user_surname, user_emergency_contact, user_status))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def report_user_logins():
    users_object = get_users()
    users = users_object.get('items')
    headers = ('Successful Logins', 'Email', 'Name', 'Surname')
    rows = []
    for user in users:
        user_email = user.get('email')
        user_name = user.get('name')
        user_surname = user.get('surname')
        user_login_metadata = user.get('userLoginMetadata')
        if user_login_metadata:
            user_successful_login_counter = f"{user_login_metadata.get('successfulLoginCounter'):010}"
            formatted_user_login_metadata = f'{user_successful_login_counter}'
        else:
            formatted_user_login_metadata = '0000000000'

        rows.append((formatted_user_login_metadata, user_email, user_name, user_surname))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower(), reverse=True)

    return headers, sorted_rows


def report_user_logins_by_name():
    user_logins_by_name = {}
    users_object = get_users()
    users = users_object.get('items')
    headers = ('Full Name', 'Email(s)', 'Logins')
    rows = []
    for user in users:
        user_email = user.get('email')
        user_name = user.get('name')
        user_surname = user.get('surname')
        # Sync up dynatrace and customer email
        if user_surname == 'Smerek':
            user_name = 'Chris'
        user_full_name = f'{user_surname}, {user_name}'
        user_login_metadata = user.get('userLoginMetadata')
        if user_login_metadata:
            user_successful_login_counter = int(user_login_metadata.get('successfulLoginCounter'))
        else:
            user_successful_login_counter = 0
        if user_full_name in user_logins_by_name:
            user = user_logins_by_name.get(user_full_name)
            user_emails = user.get('emails')
            user_emails.append(user_email)
            user_logins = user.get('logins')
            total_logins = user_logins + user_successful_login_counter
            user_logins_by_name[user_full_name]['emails'] = user_emails
            user_logins_by_name[user_full_name]['logins'] = total_logins
        else:
            user_logins_by_name[user_full_name] = {'emails': [user_email], 'logins': user_successful_login_counter}

    for user in user_logins_by_name:
        user_info = user_logins_by_name.get(user)
        logins = user_info.get('logins')
        emails = str(user_info.get('emails')).replace("'", "").replace('[', '').replace(']', '')
        rows.append((user, emails, logins))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def report_environments():
    environments_object = get_environments()
    environments = environments_object.get('tenantResources')
    headers = ['Name', 'ID']
    rows = []
    for env in environments:
        environment_name = env.get('name')
        environment_id = env.get('id')
        rows.append((environment_name, environment_id))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def report_management_zones_in_environments():
    environments_object = get_environments()
    management_zones = environments_object.get('managementZoneResources')
    headers = ('Management Zone Name', 'ID', 'Tenant')
    rows = []
    for management_zone in management_zones:
        management_zone_name = management_zone.get('name')
        management_zone_id = management_zone.get('id')
        management_zone_parent = management_zone.get('parent')
        rows.append((management_zone_name, management_zone_id, management_zone_parent))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def report_permissions():
    permissions = get_permissions()
    headers = ['Permission ID', 'Description']
    rows = []
    for permission in permissions:
        permission_id = permission.get('id')
        permission_description = permission.get('description')
        rows.append((permission_id, permission_description))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def report_regions():
    regions = get_regions()
    headers = ['Region Name']
    rows = []
    for region in regions:
        region_name = region.get('name')
        rows.append([region_name])

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def report_time_zones():
    time_zones = get_time_zones()
    headers = ('Time Zone', 'Name')
    rows = []
    for time_zone in time_zones:
        time_zone_display_name = time_zone.get('displayName')
        time_zone_name = time_zone.get('name')
        rows.append((time_zone_display_name, time_zone_name))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def report_service_users():
    service_users_object = get_service_users()
    service_users = service_users_object.get('results')
    headers = ('User ID', 'Email', 'Name', 'Surname', 'Emergency Contact', 'Status', 'Successful Logins', 'Failed Logins', 'Last Successful Login', 'Last Failed Login', 'Reset Password Token Sent', 'Last Successful Basic Authentication', 'Created', 'Updated')
    rows = []
    for service_user in service_users:
        service_user_uid = service_user.get('uid')
        service_user_email = service_user.get('email')
        service_user_name = service_user.get('name')
        service_user_surname = service_user.get('surname')
        service_user_emergency_contact = service_user.get('emergencyContact')
        service_user_status = service_user.get('userStatus')
        service_user_login_metadata = service_user.get('userLoginMetadata')
        if service_user_login_metadata:
            service_user_successful_login_counter = service_user_login_metadata.get('successfulLoginCounter')
            service_user_failed_login_counter = service_user_login_metadata.get('failedLoginCounter')
            service_user_last_successful_login = service_user_login_metadata.get('lastSuccessfulLogin')
            service_user_last_failed_login = service_user_login_metadata.get('lastFailedLogin')
            service_user_reset_password_token_sent_at = service_user_login_metadata.get('resetPasswordTokenSentAt')
            service_user_last_successful_basic_authentication = service_user_login_metadata.get('lastSuccessfulBasicAuthentication')
            service_user_created_at = service_user_login_metadata.get('createdAt')
            service_user_updated_at = service_user_login_metadata.get('updatedAt')
            formatted_service_user_login_metadata = f'{service_user_successful_login_counter}|{service_user_failed_login_counter}|{service_user_last_successful_login}|{service_user_last_failed_login}|{service_user_reset_password_token_sent_at}|{service_user_last_successful_basic_authentication}|{service_user_created_at}|{service_user_updated_at}'
        else:
            formatted_service_user_login_metadata = ''

        rows.append((service_user_uid, service_user_email, service_user_name, service_user_surname, service_user_emergency_contact, service_user_status, formatted_service_user_login_metadata))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_rows


def report_subscriptions():
    subscriptions_object = get_subscriptions()
    subscriptions = subscriptions_object.get('tenantResources')
    headers = ('Name', 'Subscription ID')
    rows = []
    for subscription in subscriptions:
        subscription_name = subscription.get('name')
        subscription_id = subscription.get('id')
        rows.append((subscription_name, subscription_id))

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

    headers, rows = report_groups()
    append_report('Groups', headers, rows, tuple_lists)

    headers, rows = report_permissions()
    append_report('Permissions', headers, rows, tuple_lists)

    headers, rows = report_users()
    append_report('Users', headers, rows, tuple_lists)

    if not skip_slow_api_calls:
        headers, rows = report_permissions_for_groups(only_show_missing_permissions=False)
        append_report('Permissions for Groups', headers, rows, tuple_lists)
        headers, rows = report_users_in_groups(only_show_missing_users=False)
        append_report('Users for Groups', headers, rows, tuple_lists)

    headers, rows = report_user_logins()
    append_report('User Logins', headers, rows, tuple_lists)

    headers, rows = report_user_logins_by_name()
    append_report('User Logins By Name', headers, rows, tuple_lists)

    headers, rows = report_management_zones_in_environments()
    append_report('Management Zones', headers, rows, tuple_lists)

    headers, rows = report_environments()
    append_report('Environments', headers, rows, tuple_lists)

    headers, rows = report_regions()
    append_report('Regions', headers, rows, tuple_lists)

    headers, rows = report_time_zones()
    append_report('Time Zones', headers, rows, tuple_lists)

    # These calls currently do nothing useful
    # Always empty results
    # headers, rows = report_service_users()
    # append_report('Service Users', headers, rows, tuple_lists)
    # Endpoint results in 404
    # headers, rows = report_subscriptions()
    # append_report('Subscriptions', headers, rows, tuple_lists)

    # Write Reports
    report_writer.initialize_text_file(None)
    report_writer.write_console_group(console_tuple_list)
    report_writer.write_text_group(None, console_tuple_list)
    report_writer.write_xlsx_worksheets(None, worksheet_tuple_list)
    report_writer.write_html_group(None, html_tuple_list)


if __name__ == '__main__':
    process()
