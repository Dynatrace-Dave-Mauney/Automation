import os

from Reuse import environment
from Reuse import user_management_api

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

scope = 'account-idm-read account-idm-write'
oauth_bearer_token = user_management_api.get_oauth_bearer_token(client_id, client_secret, scope)


def get_groups():
    r = user_management_api.get_account_management_api(oauth_bearer_token, 'groups', account_id=account_id)
    return r.json()


def delete_user_group(user_group_id):
    url = f'https://api.dynatrace.com/iam/v1/accounts/{account_id}/groups/{user_group_id}'
    r = user_management_api.delete(oauth_bearer_token, url)
    if r.status_code != 200:
        print(f'DELETE Request to Account Management API "/iam/v1/accounts/{account_id}/groups/{user_group_id}" Endpoint Failed:')
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
        if group_description == 'User Group created via automation':
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


def process():
    delete_count = 0
    group_uuid_list, rows = get_groups_to_be_deleted()

    for group_uuid in group_uuid_list:
        delete_user_group(group_uuid)
        delete_count += 1

    print(f'Deleted {delete_count} groups')


if __name__ == '__main__':
    process()
