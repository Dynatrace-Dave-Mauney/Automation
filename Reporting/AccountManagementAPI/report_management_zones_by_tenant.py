# import json
import os
import requests

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

# First, try to get the new/improved names
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


def report_management_zones_in_environments():
    environments_object = get_environments()
    management_zones = environments_object.get('managementZoneResources')
    headers = ['Management Zone Name']
    prod_rows = []
    preprod_rows = []
    dev_rows = []
    for management_zone in management_zones:
        management_zone_name = management_zone.get('name')
        # management_zone_id = management_zone.get('id')
        management_zone_parent = management_zone.get('parent')
        # management_zone_description = get_management_zone_description(management_zone_parent, management_zone_id)
        # if management_zone_description and 'wner' in management_zone_description:
        #     rows.append((management_zone_name, management_zone_id, management_zone_parent, management_zone_description))

        if management_zone_parent == prod_tenant:
            prod_rows.append([management_zone_name])
        else:
            if management_zone_parent == preprod_tenant:
                preprod_rows.append([management_zone_name])
            else:
                if management_zone_parent == dev_tenant:
                    dev_rows.append([management_zone_name])

    sorted_prod_rows = sorted(prod_rows, key=lambda row: str(row[0]).lower())
    sorted_preprod_rows = sorted(preprod_rows, key=lambda row: str(row[0]).lower())
    sorted_dev_rows = sorted(dev_rows, key=lambda row: str(row[0]).lower())

    return headers, sorted_prod_rows, sorted_preprod_rows, sorted_dev_rows


def get_management_zone_description(parent, management_zone_id):
    token = tenant_token_dict[parent]
    endpoint = '/api/config/v1/managementZones'
    r = dynatrace_api.get_without_pagination(f'https://{parent}.live.dynatrace.com{endpoint}/{management_zone_id}', token)
    management_zone = r.json()
    description = management_zone.get('description', '')
    return description


def append_report(report_name, headers, rows, tuple_lists):
    console_tuple_list, worksheet_tuple_list, html_tuple_list = tuple_lists
    console_tuple_list.append((report_name, headers, rows, '|'))
    worksheet_tuple_list.append((report_name, headers, rows, None, None))
    html_tuple_list.append((report_name, headers, rows))


def process():
    headers, prod_rows, preprod_rows, dev_rows = report_management_zones_in_environments()
    console_tuple_list = []
    worksheet_tuple_list = []
    html_tuple_list = []
    tuple_lists = [console_tuple_list, worksheet_tuple_list, html_tuple_list]
    append_report('Management Zones', headers, prod_rows, tuple_lists)
    report_writer.initialize_text_file('report_management_zones_by_tenant_prod.txt')
    report_writer.write_console_group(console_tuple_list)
    report_writer.write_text_group('report_management_zones_by_tenant_prod.txt', console_tuple_list)

    console_tuple_list = []
    worksheet_tuple_list = []
    html_tuple_list = []
    tuple_lists = [console_tuple_list, worksheet_tuple_list, html_tuple_list]
    append_report('Management Zones', headers, preprod_rows, tuple_lists)
    report_writer.initialize_text_file('report_management_zones_by_tenant_preprod.txt')
    report_writer.write_console_group(console_tuple_list)
    report_writer.write_text_group('report_management_zones_by_tenant_preprod.txt', console_tuple_list)

    console_tuple_list = []
    worksheet_tuple_list = []
    html_tuple_list = []
    tuple_lists = [console_tuple_list, worksheet_tuple_list, html_tuple_list]
    append_report('Management Zones', headers, dev_rows, tuple_lists)
    report_writer.initialize_text_file('report_management_zones_by_tenant_dev.txt')
    report_writer.write_console_group(console_tuple_list)
    report_writer.write_text_group('report_management_zones_by_tenant_dev.txt', console_tuple_list)

    # Write Reports
    # report_writer.write_xlsx_worksheets(None, worksheet_tuple_list)
    # report_writer.write_html_group(None, html_tuple_list)


if __name__ == '__main__':
    process()
