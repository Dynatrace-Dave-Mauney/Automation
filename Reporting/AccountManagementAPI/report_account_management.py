import json
import os
import requests

# Reporting for: https://api.dynatrace.com/spec/

# Creating an OAuth Client:
# Access Account Settings/Identity & access management/OAuth clients
# https://myaccount.dynatrace.com/account/iam/api?account-uuid=**********
# Click "Create client" link at bottom of page

# Permissions Needed: All Under Account
# account-idm-read, account-idm-write, account-env-read, account-env-write, account-uac-read, account-uac-write,
# iam-policies-management, iam:policies:write, iam:policies:read, iam:bindings:write, iam:bindings:read,
# iam:effective-permissions:read

# https://www.dynatrace.com/support/help/shortlink/account-api#api-explorer
# Open the User menu and select Account settings (in latest Dynatrace, Account Management).
# On the top navigation bar, go to Identity & access management > OAuth clients.
# In the upper-right corner of the page, select Account Management API.

account_id = os.getenv('ACCOUNTID')
client_secret = os.getenv('CLIENT_SECRET')
client_id = os.getenv('CLIENT_ID')

print('Masked environment variables:')
print(f'account_id: {account_id[:10]}*')
print(f'client_secret: {client_secret[:5]}*{client_secret[70:]}')
print(f'client_id {client_id[:10]}*')

def get_groups():
    r = get_account_management_api('groups')
    return json.loads(r.text)


def get_permissions_for_group(group_uuid):
    api_type = f'groups/{group_uuid}/permissions'
    r = get_account_management_api(api_type)
    return json.loads(r.text)


def get_users_in_group(group_uuid):
    api_type = f'groups/{group_uuid}/users'
    r = get_account_management_api(api_type)
    return json.loads(r.text)


def get_users():
    r = get_account_management_api('users')
    return json.loads(r.text)


def get_service_users():
    r = get_account_management_api('service-users')
    return json.loads(r.text)


def get_environments():
    r = get_account_management_api('environments')
    return json.loads(r.text)


def get_subscriptions():
    r = get_account_management_api('subscriptions')
    return json.loads(r.text)


def get_time_zones():
    r = get_account_management_api('time-zones')
    return json.loads(r.text)


def get_regions():
    r = get_account_management_api('regions')
    return json.loads(r.text)


def get_permissions():
    r = get_account_management_api('permissions')
    return json.loads(r.text)


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
        oauth_bearer_token = json.loads(r.text)["access_token"]
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
    print('group_name|group_federated_attribute_values|group_uuid|group_owner|group_description|group_hidden|group_created_at|group_updated_at')
    lines = []
    for group in groups:
        group_uuid = group.get('uuid')
        group_name = group.get('name')
        group_owner = group.get('owner')
        group_description = group.get('description')
        group_federated_attribute_values = group.get('federatedAttributeValues')
        group_hidden = group.get('hidden')
        group_created_at = group.get('createdAt')
        group_updated_at = group.get('updatedAt')
        lines.append(f'{group_name}|{group_federated_attribute_values}|{group_uuid}|{group_owner}|{group_description}|{group_hidden}|{group_created_at}|{group_updated_at}')

    for line in sorted(lines):
        print(line)


def report_permissions_for_groups(only_show_missing_permissions):
    groups_object = get_groups()
    groups = groups_object.get('items')
    sorted_groups = sorted(groups, key=lambda x: x['name'])

    print('group_name|group_uuid|permission_name|permission_scope|permission_scope_type|permission_created_at|permission_updated_at')
    group_count = 0
    for group in sorted_groups:
        lines = []
        group_count += 1
        # Modify limit for testing...
        if group_count < 999999:
            group_uuid = group.get('uuid')
            group_name = group.get('name')
            # print(f'Processing group name: {group_name} with count of {group_count}')
            permissions_object = get_permissions_for_group(group_uuid)
            permissions = permissions_object.get('permissions')
            # Want to report only groups with permissions?  Comment out the section below...
            if not permissions:
                lines.append(f'{group_name}|{group_uuid}|No Permissions!')
            if not only_show_missing_permissions:
                for permission in permissions:
                    permission_name = permission.get('permissionName')
                    permission_scope = permission.get('scope')
                    permission_scope_type = permission.get('scopeType')
                    permission_created_at = permission.get('createdAt')
                    permission_updated_at = permission.get('updatedAt')
                    lines.append(f'{group_name}|{group_uuid}|{permission_name}|{permission_scope}|{permission_scope_type}|{permission_created_at}|{permission_updated_at}')

            for line in sorted(lines):
                print(line)


def report_users_in_groups(only_show_missing_users):
    groups_object = get_groups()
    groups = groups_object.get('items')
    sorted_groups = sorted(groups, key=lambda x: x['name'])
    print('group_name|group_uuid|user_id|user_email|user_name|user_surname|user_emergency_contact|user_status')
    group_count = 0
    for group in sorted_groups:
        lines = []
        group_count += 1
        # Modify limit for testing...
        if group_count <= 999999999:
            group_uuid = group.get('uuid')
            group_name = group.get('name')
            # print(f'Processing group name: {group_name} with count of {group_count}')
            users_object = get_users_in_group(group_uuid)
            users = users_object.get('items')
            # Want to report only groups with users?  Comment out the section below...
            if not users:
                lines.append(f'{group_name}|{group_uuid}|No users!')
            if not only_show_missing_users:
                for user in users:
                    user_id = user.get('uid')
                    user_email = user.get('email')
                    user_name = user.get('name')
                    user_surname = user.get('surname')
                    user_emergency_contact = user.get('emergencyContact')
                    user_status = user.get('userStatus')
                    lines.append(f'{group_name}|{group_uuid}|{user_id}|{user_email}|{user_name}|{user_surname}|{user_emergency_contact}|{user_status}')

            for line in sorted(lines):
                print(line)


def report_users():
    users_object = get_users()
    users = users_object.get('items')
    print('uid|email|name|surname|emergencyContact|userStatus|successfulLoginCounter|failedLoginCounter|lastSuccessfulLogin|lastFailedLogin|resetPasswordTokenSentAt|lastSuccessfulBasicAuthentication|createdAt|updatedAt')
    lines = []
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
            formatted_user_login_metadata = f'{user_successful_login_counter}|{user_failed_login_counter}|{user_last_successful_login}|{user_last_failed_login}|{user_reset_password_token_sent_at}|{user_last_successful_basic_authentication}|{user_created_at}|{user_updated_at}'
        else:
            formatted_user_login_metadata = ''

        lines.append(f'{user_uid}|{user_email}|{user_name}|{user_surname}|{user_emergency_contact}|{user_status}|{formatted_user_login_metadata}')

    for line in sorted(lines):
        print(line)


def report_user_logins():
    users_object = get_users()
    users = users_object.get('items')
    print('successfulLoginCounter|email|name|surname')
    lines = []
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

        lines.append(f'{formatted_user_login_metadata}|{user_email}|{user_name}|{user_surname}')

    for line in sorted(lines, reverse=True):
        print(line)


def report_user_logins_by_name():
    user_logins_by_name = {}
    users_object = get_users()
    users = users_object.get('items')
    print('logins|full name|email(s)')
    lines = []
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
        lines.append(f"{logins: 6}|{user}|{emails}")

    for line in sorted(lines, reverse=True):
        print(line)


def report_service_users():
    service_users_object = get_service_users()
    service_users = service_users_object.get('items')
    print('uid|email|name|surname|emergencyContact|userStatus|successfulLoginCounter|failedLoginCounter|lastSuccessfulLogin|lastFailedLogin|resetPasswordTokenSentAt|lastSuccessfulBasicAuthentication|createdAt|updatedAt')
    lines = []
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

        lines.append(f'{service_user_uid}|{service_user_email}|{service_user_name}|{service_user_surname}|{service_user_emergency_contact}|{service_user_status}|{formatted_service_user_login_metadata}')

    for line in sorted(lines):
        print(line)


def report_subscriptions():
    subscriptions_object = get_subscriptions()
    subscriptions = subscriptions_object.get('tenantResources')
    print('name|id')
    lines = []
    for subscription in subscriptions:
        subscription_name = subscription.get('name')
        subscription_id = subscription.get('id')
        lines.append(f'{subscription_name}|{subscription_id}')

    for line in sorted(lines):
        print(line)

    
def report_management_zones_in_environments():
    environments_object = get_environments()
    management_zones = environments_object.get('managementZoneResources')
    print('name|id|parent')
    lines = []
    for management_zone in management_zones:
        management_zone_name = management_zone.get('name')
        management_zone_id = management_zone.get('id')
        management_zone_parent = management_zone.get('parent')
        lines.append(f'{management_zone_name}|{management_zone_id}|{management_zone_parent}')

    for line in sorted(lines):
        print(line)


def report_environments():
    environments_object = get_environments()
    environments = environments_object.get('tenantResources')
    print('name|id')
    lines = []
    for environment in environments:
        environment_name = environment.get('name')
        environment_id = environment.get('id')
        lines.append(f'{environment_name}|{environment_id}')

    for line in sorted(lines):
        print(line)


def report_time_zones():
    time_zones = get_time_zones()
    print('displayName|name')
    lines = []
    for time_zone in time_zones:
        time_zone_display_name = time_zone.get('displayName')
        time_zone_name = time_zone.get('name')
        lines.append(f'{time_zone_display_name}|{time_zone_name}')

    for line in sorted(lines):
        print(line)


def report_regions():
    regions = get_regions()
    print('name')
    lines = []
    for region in regions:
        region_name = region.get('name')
        lines.append(f'{region_name}')

    for line in sorted(lines):
        print(line)


def report_permissions():
    permissions = get_permissions()
    print('id|description')
    lines = []
    for permission in permissions:
        permission_id = permission.get('id')
        permission_description = permission.get('description')
        lines.append(f'{permission_id}|{permission_description}')

    for line in sorted(lines):
        print(line)


def process():
    print('Groups')
    report_groups()
    print('')

    print('Users')
    report_users()
    print('')

    print('User Logins')
    report_user_logins()
    print('')

    print('User Logins by Name')
    report_user_logins_by_name()
    print('')

    # print('Permissions for Groups (missing only)')
    # report_permissions_for_groups(only_show_missing_permissions=True)
    print('Permissions for Groups')
    report_permissions_for_groups(only_show_missing_permissions=False)
    print('')

    # print('Users in Groups (missing only)')
    # report_users_in_groups(only_show_missing_users=True)
    print('Users in Groups')
    report_users_in_groups(only_show_missing_users=False)
    print('')

    print('Environments')
    report_environments()
    print('')

    print('Management Zones in Environments')
    report_management_zones_in_environments()
    print('')

    print('Time Zones')
    report_time_zones()
    print('')

    print('Regions')
    report_regions()
    print('')

    print('Permissions')
    report_permissions()
    print('')

    # These calls currently return 403-Forbidden
    # report_service_users()
    # report_subscriptions()


if __name__ == '__main__':
    process()
