# Uses "[Owner:abcde]" as the "Management Zone Group" indicator
# NOTE: BE SURE TO CHANGE TARGETS (ON AROUND LINE 45)
# EXAMPLE:
# target_environment_list = [prod_tenant, preprod_tenant, dev_tenant]

import json
import os
import requests

from Reuse import dynatrace_api
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

tenant_token_dict = {prod_tenant: prod_token, preprod_tenant: preprod_token, dev_tenant: dev_token, sandbox_tenant: sandbox_token}

target_environment_list = [prod_tenant, preprod_tenant, dev_tenant]

scope = 'account-idm-read account-idm-write'


def get_environments():
    oauth_bearer_token = user_management_api.get_oauth_bearer_token(client_id, client_secret, scope)
    r = user_management_api.get_account_management_api(oauth_bearer_token, 'environments', account_id=account_id)
    return r.json()


def process():
    user_group_dict = load_user_group_dict()

    # for key in user_group_dict.keys():
    #     print(key, user_group_dict[key])
    # exit(1111)

    for key in user_group_dict.keys():
        user_group_name = key
        r = post_user_group(user_group_name)
        user_group_uuid = json.loads(r.text)[0].get('uuid')
        if not user_group_uuid:
            print(f'Failed to get user group uuid from response object text after post_user_group for group {user_group_name}: {r.text}')
        else:
            for management_zone_dict in user_group_dict[key]:
                management_zone_id = management_zone_dict['id']
                management_zone_name = management_zone_dict['name']
                management_zone_parent = management_zone_dict['parent']
                post_log_viewer_permission(user_group_name, user_group_uuid, management_zone_name, management_zone_id, management_zone_parent)


def load_user_group_dict():
    user_group_dict = {}

    endpoint = '/api/config/v1/managementZones'

    for target_environment in target_environment_list:
        env = f'https://{target_environment}.live.dynatrace.com'
        token = tenant_token_dict[target_environment]
        management_zones_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
        for management_zones_json in management_zones_json_list:
            inner_management_zones_json_list = management_zones_json.get('values')
            for inner_management_zones_json in inner_management_zones_json_list:
                management_zone_id = inner_management_zones_json.get('id')
                management_zone_name = inner_management_zones_json.get('name')
                endpoint = '/api/config/v1/managementZones'
                r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{management_zone_id}', token)
                management_zone = r.json()
                user_group_name = f'ODFL Log Viewer - {management_zone_name}'
                upsert_user_group_dict(user_group_name, management_zone_id, management_zone_name, target_environment, user_group_dict)
                description = management_zone.get('description', '')
                if description and '[Owner:' in description:
                    mzg_start = description.find('[') + 7
                    mzg_end = description.find(']')
                    mzg = description[mzg_start:mzg_end].strip()
                    user_group_name = f'ODFL Log Viewer - {mzg}'
                    upsert_user_group_dict(user_group_name, management_zone_id, management_zone_name, target_environment, user_group_dict)

    return user_group_dict


def upsert_user_group_dict(user_group_name, management_zone_id, management_zone_name, management_zone_parent, user_group_dict):
    target_management_zone_list_value = {'id': management_zone_id, 'name': management_zone_name, 'parent': management_zone_parent}
    if user_group_dict.get(user_group_name):
        user_group_dict[user_group_name].append(target_management_zone_list_value)
    else:
        user_group_dict[user_group_name] = [target_management_zone_list_value]
        
    return user_group_dict
        

def post_user_group(user_group_name):
    user_group_dict = [{
        "name": user_group_name,
        "description": f'User Group created via automation',
    }]

    r = None
    try:
        url = f'https://api.dynatrace.com/iam/v1/accounts/{account_id}/groups'
        oauth_bearer_token = user_management_api.get_oauth_bearer_token(client_id, client_secret, scope)
        r = user_management_api.post(oauth_bearer_token, url, json.dumps(user_group_dict))
        if 200 < r.status_code < 299:
            print(f'post_user_group for group {user_group_name} response status code: {r.status_code}')
        else:
            if r.status_code == 400:
                print(f'post_user_group for group {user_group_name} failed with response status code {r.status_code}: duplicate')
                r.raise_for_status()
            else:
                print(f'post_user_group for group {user_group_name} failed with response status code {r.status_code}:{r.text}')
                r.raise_for_status()
        return r
    except requests.exceptions.RequestException as e:
        print(f'post_user_group for group {user_group_name} failed with response status code: {r.status_code}')
        print("Please check the following HTTP response to troubleshoot the issue: ")
        print(r.text)
        print("Exiting Program")
        raise SystemExit(e)


def post_log_viewer_permission(user_group_name, user_group_id, management_zone_name, management_zone_id, management_zone_parent):
    print(f'post_log_viewer_permission({user_group_name}, {user_group_id}, {management_zone_name}, {management_zone_id}, {management_zone_parent}')
    permission_scope = f'{management_zone_parent}:{management_zone_id}'
    permissions_list = [
            {'permissionName': 'tenant-logviewer', 'scope': permission_scope, 'scopeType': 'management-zone'},
            {'permissionName': 'tenant-viewer', 'scope': permission_scope, 'scopeType': 'management-zone'}
    ]

    r = None

    try:
        url = f'https://api.dynatrace.com/iam/v1/accounts/{account_id}/groups/{user_group_id}/permissions'
        oauth_bearer_token = user_management_api.get_oauth_bearer_token(client_id, client_secret, scope)
        r = user_management_api.post(oauth_bearer_token, url, json.dumps(permissions_list))
        r.raise_for_status()
        print(f'post_log_viewer_permission for group/management zone {user_group_name}/{management_zone_name} response status code: {r.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'post_log_viewer_permission for group/management zone {user_group_name}/{management_zone_name} failed with response status code: {r.status_code}')
        print("Please check the following HTTP response to troubleshoot the issue: ")
        print(r.text)
        print("Exiting Program")
        raise SystemExit(e)


if __name__ == '__main__':
    process()
