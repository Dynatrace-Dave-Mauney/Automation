import os
import requests

from inspect import currentframe
from json.decoder import JSONDecodeError

# env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
# env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

tenant = os.environ.get(tenant_key)
token = os.environ.get(token_key)
env = f'https://{tenant}.live.dynatrace.com'


def get_rest_api_json(url, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    # print(f'Response Text {resp.text}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    try:
        json = resp.json()

        # Some json is just a list of dictionaries.
        # Config V1 AWS Credentials is the only example I am aware of.
        # For these, I have never seen pagination.
        if type(json) is list:
            # DEBUG:
            # print(json)
            return json

        json_list = [json]

        next_page_key = json.get('nextPageKey')

        while next_page_key is not None:
            # print(f'next_page_key: {next_page_key}')
            params = {'nextPageKey': next_page_key}
            full_url = url + endpoint
            resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
            # print(resp.url)

            if resp.status_code != 200:
                print('Paginated REST API Call Failed!')
                print(f'GET {full_url} {resp.status_code} - {resp.reason}')
                exit(1)

            json = resp.json()
            # print(json)

            next_page_key = json.get('nextPageKey')
            json_list.append(json)

        return json_list

    except JSONDecodeError:
        print('JSON decode error. Response: ')
        print(resp)
        print(resp.text)
        exit(get_line_number())


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def process():
    mda_dict = {}

    # Note 'mdaId' is in the list solely to check for any MDA reference beyond the targets listed below it
    mda_list = [
        'mdaId',
        'dd458841-9bbe-4d3e-bb5e-5562e3420f8b',
        '144b80d2-dbf6-46e5-97d8-2d30355cde58',
        'c1b30b11-db5c-42f8-a67f-691496788ad9',
        '48ec22c7-3350-409f-aa2e-9500c3db81c9',

    ]
    for mda in mda_list:
        mda_dict[mda] = {'dashboards': []}

    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboards_json_list = get_rest_api_json(env, endpoint, params)
    dashboard_id_list = []
    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')
            dashboard_id_list.append(entity_id)
    for dashboard_id in sorted(dashboard_id_list):
        dashboard_json = get_rest_api_json(env, endpoint + '/' + dashboard_id, params)
        for dashboard in dashboard_json:
            dashboard_metadata = dashboard.get('dashboardMetadata')
            name = dashboard_metadata.get('name')
            for mda in sorted(mda_list):
                if mda in str(dashboard):
                    try:
                        print(f'MDA {mda} found in dashboard {name}')
                        dashboard_list = mda_dict[mda].get('dashboards')
                        if name not in dashboard_list:
                            dashboard_list.append(name)
                            mda_dict[mda]['dashboards'] = dashboard_list
                    except KeyError:
                        print(f'MDA {mda} found in dashboard {name} but not in target list')

    display_findings(mda_dict)


def display_findings(mda_dict):
    # print(mda_dict)
    print('Findings:')
    keys = sorted(mda_dict.keys())
    for key in keys:
        # print(key)
        mda_xref = mda_dict[key]
        # print(mda_xref)
        mda_xref_keys = mda_xref.keys()
        for mda_xref_key in mda_xref_keys:
            # print(mda_xref_key)
            if len(mda_xref[mda_xref_key]) > 0:
                print(key + ' used in ' + mda_xref_key + ': ' + sort_and_stringify_list_items(mda_xref[mda_xref_key]))


def sort_and_stringify_list_items(any_list):
    list_str = str(sorted(any_list))
    list_str = list_str.replace('[', '')
    list_str = list_str.replace(']', '')
    list_str = list_str.replace("'", "")
    list_str = list_str.replace(' ', '')
    return list_str


if __name__ == '__main__':
    process()
