import os
import requests
import urllib.parse


from inspect import currentframe
from json.decoder import JSONDecodeError

env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
# env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

tenant = os.environ.get(tenant_key)
token = os.environ.get(token_key)
env = f'https://{tenant}.live.dynatrace.com'


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    json_data = resp.json()

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json_data) is list:
        # DEBUG:
        # print(json_data)
        return json_data

    json_list = [json_data]
    next_page_key = json_data.get('nextPageKey')

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

        json_data = resp.json()
        # print(json_data)

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list



def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def process():
    dashboard_details = load_dashboard_details()

    endpoint = '/api/v2/metrics/query'
    metric_schema_id = 'builtin:dashboards.viewCount'
    metric_query_options = ':splitBy("id"):avg:auto:sort(value(avg,descending)):fold:limit(100)'
    from_time = 'now-1M'
    params = 'metricSelector=' + urllib.parse.quote(metric_schema_id) + metric_query_options + '&from=' + from_time
    metrics_json_list = get_rest_api_json(env, token, endpoint, params)
    for metrics_json in metrics_json_list:
        result_list = metrics_json.get('result')
        for result in result_list:
            data = result.get('data')
            for datapoint in data:
                values = datapoint.get('values')[0]
                dashboard_id = datapoint.get('dimensionMap').get('id').strip()
                dashboard_detail = dashboard_details.get(dashboard_id)
                if dashboard_detail:
                    dashboard_name = dashboard_detail.get('name', '')
                    dashboard_owner = dashboard_detail.get('owner', '')
                else:
                    dashboard_name = '*** DELETED ***'
                    dashboard_owner = ''
                print(dashboard_name + '|' + dashboard_id  + '|' + dashboard_owner + '|' + str(values))


def load_dashboard_details():
    dashboard_details = {}

    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboards_json_list = get_rest_api_json(env, token, endpoint, params)
    # print(dashboards_json_list)

    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')
            name = inner_dashboards_json.get('name')
            owner = inner_dashboards_json.get('owner')
            dashboard_details[entity_id] = {'name': name, 'owner': owner}

    return dashboard_details

if __name__ == '__main__':
    process()
