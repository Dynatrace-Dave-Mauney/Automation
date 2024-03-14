import json
import os
import requests

from Reuse import dynatrace_api
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

# configuration_path = 'configurations.yaml'
# if os.path.isfile(configuration_path):
#     account_id = environment.get_configuration('account_id', configuration_file=configuration_path)
#     client_id = environment.get_configuration('client_id', configuration_file=configuration_path)
#     client_secret = environment.get_configuration('client_secret', configuration_file=configuration_path)
#     skip_slow_api_calls = environment.get_configuration('skip_slow_api_calls', configuration_file=configuration_path)
#     environment_variable_source = 'Configuration File'

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


def get_environments():
    r = get_account_management_api('environments')
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


def process():
    target_environment_list = [sandbox_tenant]

    target_management_zone_by_mzg_dict = {}

    target_management_zone_dict = get_management_zones_for_target_environments(target_environment_list)

    target_management_zone_keys = target_management_zone_dict.keys()
    for target_management_zone_key in target_management_zone_keys:
        management_zone_id = target_management_zone_key
        management_zone_name = target_management_zone_dict[management_zone_id]['name']
        management_zone_parent = target_management_zone_dict[management_zone_id]['parent']
        post_user_group([management_zone_id], management_zone_name, management_zone_parent)

        management_zone_mzg = target_management_zone_dict[management_zone_id]['mzg']
        if management_zone_mzg:
            mzg_list = target_management_zone_by_mzg_dict.get(management_zone_mzg, [])
            mzg_list.append({'id': management_zone_id, 'name': management_zone_name, 'parent': management_zone_parent})
            # mzg_list.append(management_zone_id)
            target_management_zone_by_mzg_dict[management_zone_mzg] = mzg_list

    for target_management_zone_by_mzg_key in target_management_zone_by_mzg_dict.keys():
        mz_id_list = []
        target_management_zone_by_mzg_list = target_management_zone_by_mzg_dict[target_management_zone_by_mzg_key]
        for target_management_zone_by_mzg in target_management_zone_by_mzg_list:
            mz_id = target_management_zone_by_mzg.get('id')
            mz_id_list.append(mz_id)
        mz_parent = target_management_zone_by_mzg_list[0].get('parent')
        post_user_group(mz_id_list, target_management_zone_by_mzg_key, mz_parent)


def get_management_zones_for_target_environments(target_environment_list):
    target_management_zone_dict = {}

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
                description = management_zone.get('description', '')
                mzg = None
                if '[MZG:' in description:
                    mzg_start = description.find('[') + 5
                    mzg_end = description.find(']')
                    mzg = description[mzg_start:mzg_end]
                target_management_zone_dict[management_zone_id] = {'name': management_zone_name, 'parent': target_environment, 'mzg': mzg}

    return target_management_zone_dict


def post_user_group(management_zone_id_list, management_zone_name, management_zone_parent, **kwargs):

    is_mz_group = False

    if kwargs:
        is_mz_group = kwargs.get('is_mz_group', False)

    oauth_bearer_token = get_oauth_bearer_token()

    user_group_name = f'ODFL Log Viewer - {management_zone_name}'

    if is_mz_group:
        desc_mz_literal = 'management zone group'
    else:
        desc_mz_literal = 'management zone'

    user_group_dict = [{
        "name": user_group_name,
        "description": f'User Group created for {desc_mz_literal} "{management_zone_name}" via automation',
        # Claim is not needed
        # "federatedAttributeValues": [user_group_name]
    }]

    headers = {'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + oauth_bearer_token}
    try:
        r = requests.post(f'https://api.dynatrace.com/iam/v1/accounts/{account_id}/groups', data=json.dumps(user_group_dict), headers=headers)
        if 200 < r.status_code < 299:
            print(f'post_user_group for group {user_group_name} response status code: {r.status_code}')
        else:
            if r.status_code == 400:
                print(f'post_user_group for group {user_group_name} to tenant {management_zone_parent} failed with response status code {r.status_code}: duplicate')
            else:
                print(f'post_user_group for group {user_group_name} to tenant {management_zone_parent} failed with response status code {r.status_code}:{r.text}')
                r.raise_for_status()
        if 200 < r.status_code < 299:
            user_group_id = json.loads(r.text)[0].get('uuid')
            if user_group_id:
                put_log_viewer_permission(user_group_name, user_group_id, management_zone_id_list, management_zone_parent)
            else:
                print(f'Failed to get user group id from response object text after post_user_group to tenant {management_zone_parent} for group {user_group_name}: {r.text}')
    except requests.exceptions.RequestException as e:
        print(f'post_user_group for group {user_group_name} to tenant {management_zone_parent} failed with response status code: {r.status_code}')
        print("Please check the following HTTP response to troubleshoot the issue: ")
        print(r.text)
        print("Exiting Program")
        raise SystemExit(e)


def put_log_viewer_permission(user_group_name, user_group_id, management_zone_id_list, management_zone_parent):
    oauth_bearer_token = get_oauth_bearer_token()

    permissions_list = []

    for management_zone_id in management_zone_id_list:
        scope = f'{management_zone_parent}:{management_zone_id}'
        permissions_list.append({'permissionName': 'tenant-logviewer', 'scope': scope, 'scopeType': 'management-zone'})
        permissions_list.append({'permissionName': 'tenant-viewer', 'scope': scope, 'scopeType': 'management-zone'})

    # print(management_zone_id_list, permissions_list)

    headers = {'accept': '*/*', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + oauth_bearer_token}

    try:
        r = requests.post(f'https://api.dynatrace.com/iam/v1/accounts/{account_id}/groups/{user_group_id}/permissions', data=json.dumps(permissions_list), headers=headers)
        r.raise_for_status()
        print(f'put_log_viewer_permission for group {user_group_name} response status code: {r.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'put_log_viewer_permission for group {user_group_name} to tenant {management_zone_parent}  failed with response status code: {r.status_code}')
        print("Please check the following HTTP response to troubleshoot the issue: ")
        print(r.text)
        print("Exiting Program")
        raise SystemExit(e)


if __name__ == '__main__':
    process()
