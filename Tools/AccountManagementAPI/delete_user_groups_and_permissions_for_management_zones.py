import os
import requests

from Reuse import environment


account_id = os.getenv('DYNATRACE_AUTOMATION_ACCOUNT_ID')
client_id = os.getenv('DYNATRACE_AUTOMATION_CLIENT_ID')
client_secret = os.getenv('DYNATRACE_AUTOMATION_CLIENT_SECRET')
skip_slow_api_calls = environment.get_boolean_environment_variable('SKIP_SLOW_API_CALLS', 'True')
prod_tenant = os.getenv('DYNATRACE_PROD_TENANT')
prod_token = os.getenv('DYNATRACE_AUTOMATION_PROD_TOKEN')
preprod_tenant = os.getenv('DYNATRACE_PREPROD_TENANT')
preprod_token = os.getenv('DYNATRACE_AUTOMATION_PREPROD_TOKEN')
dev_tenant = os.getenv('DYNATRACE_DEV_TENANT')
dev_token = os.getenv('DYNATRACE_AUTOMATION_DEV_TOKEN')
sandbox_tenant = os.getenv('DYNATRACE_SANDBOX_TENANT')
sandbox_token = os.getenv('DYNATRACE_AUTOMATION_SANDBOX_TOKEN')
environment_variable_source = 'New Environment Variable Names'

print('Masked environment variables:')
print(f'account_id: {account_id[:10]}*')
print(f'client_secret: {client_secret[:5]}*{client_secret[70:]}')
print(f'client_id: {client_id[:10]}*')
print(f'skip_slow_api_calls: {skip_slow_api_calls}')
print(f'prod_tenant: {prod_tenant}')
print(f'prod_token: {prod_token[:40]}')
print(f'preprod_tenant: {preprod_tenant}')
print(f'preprod_token: {preprod_token[:40]}')
print(f'dev_tenant: {dev_tenant}')
print(f'dev_token: {dev_token[:40]}')
print(f'sandbox_tenant: {sandbox_tenant}')
print(f'sandbox_token: {sandbox_token[:40]}')
print(f'environment_variable_source: {environment_variable_source}')


def get_groups():
    r = get_account_management_api('groups')
    return r.json()


def get_permissions_for_group(group_uuid):
    api_type = f'groups/{group_uuid}/permissions'
    r = get_account_management_api(api_type)
    return r.json()


def get_permissions():
    r = get_account_management_api('permissions')
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


def delete_user_group(user_group_id):
    oauth_bearer_token = get_oauth_bearer_token()
    url = f'https://api.dynatrace.com/iam/v1/accounts/{account_id}/groups/{user_group_id}'
    headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    r = requests.delete(url, headers=headers)
    if r.status_code != 200:
        print(f'DELETE Request to Account Management API "/iam/v1/accounts/{account_id}/groups/{user_group_id}" Endpoint Failed:')
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


def get_groups_to_be_deleted():
    groups_object = get_groups()
    groups = groups_object.get('items')
    group_uuid_list = []
    rows = []
    for group in groups:
        group_description = str(group.get('description'))
        if group_description.startswith('User Group created for management zone') and group_description.endswith('via automation'):
            group_uuid = str(group.get('uuid'))
            group_name = str(group.get('name'))
            group_owner = str(group.get('owner'))
            group_federated_attribute_values = str(group.get('federatedAttributeValues'))
            group_hidden = str(group.get('hidden'))
            group_created_at = str(group.get('createdAt'))
            group_updated_at = str(group.get('updatedAt'))
            rows.append((group_name, group_federated_attribute_values, group_uuid, group_owner, group_description, group_hidden, group_created_at, group_updated_at))
            group_uuid_list.append(group_uuid)

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return group_uuid_list, sorted_rows


def get_permissions_for_groups_to_be_deleted(group_uuid_list):
    groups_object = get_groups()
    groups = groups_object.get('items')
    sorted_groups = sorted(groups, key=lambda x: x['name'])
    rows = []
    for group in sorted_groups:
        group_uuid = group.get('uuid')
        if group_uuid in group_uuid_list:
            group_name = group.get('name')
            permissions_object = get_permissions_for_group(group_uuid)
            permissions = permissions_object.get('permissions')
            for permission in permissions:
                print('permission:', permission)
                permission_name = permission.get('permissionName')
                permission_scope = permission.get('scope')
                permission_scope_type = permission.get('scopeType')
                permission_created_at = permission.get('createdAt')
                permission_updated_at = permission.get('updatedAt')
                rows.append((group_name, group_uuid, permission_name, permission_scope, permission_scope_type, permission_created_at, permission_updated_at))

    sorted_rows = sorted(rows, key=lambda row: str(row[0]).lower())

    return sorted_rows


def process():
    group_uuid_list, rows = get_groups_to_be_deleted()
    for group_uuid in group_uuid_list:
        delete_user_group(group_uuid)

    # print('group_uuid_list:', group_uuid_list)
    # for group_uuid in group_uuid_list:
    #     print(group_uuid)
    #
    # print('rows:', rows)
    # for row in rows:
    #     print(row)
    #
    # permission_rows = get_permissions_for_groups_to_be_deleted(group_uuid_list)
    #
    # print('permission_rows:', permission_rows)
    # for permission_row in permission_rows:
    #     print(permission_row)


if __name__ == '__main__':
    process()
