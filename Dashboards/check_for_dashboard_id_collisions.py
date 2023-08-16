#
# Check the directory containing dashboards against the specified tenant for any dashboard id collisions
#

import os
import glob
import json

from Reuse import environment
from Reuse import dynatrace_api

known_collisions = [
    '22471a3e-4bb3-11ed-bdc3-0242ac120002',
    '3b9c20e2-dc58-4a91-8dcb-f6217dc869ac',
    '6b38732e-609c-44e2-b34d-0286717ecdab',
    '6b38732e-8c5c-4b32-80a1-7053ec8f37e1',
    '6b38732e-d26b-45c7-b107-ed85e87ff288',
    'b6fc0160-9332-454f-a7bc-7217b2ae540c',
    'c15f39a8-7d74-4b97-af28-0b17a20dc711',
    'c704bd72-92e9-452a-b40e-73e6f4df9f08',
    '22471a3e-4bb3-11ed-bdc3-0242ac120002',
    '3b9c20e2-dc58-4a91-8dcb-f6217dc869ac',
    '6b38732e-609c-44e2-b34d-0286717ecdab',
    '6b38732e-8c5c-4b32-80a1-7053ec8f37e1',
    '6b38732e-d26b-45c7-b107-ed85e87ff288',
    'b6fc0160-9332-454f-a7bc-7217b2ae540c',
    'c15f39a8-7d74-4b97-af28-0b17a20dc711',
    'c704bd72-92e9-452a-b40e-73e6f4df9f08',
]

def main():
    dashboard_id_list = []

    tenant_dict = load_tenants(['Prod', 'NonProd'])

    try:
        input_glob_pattern = f'../$Output/Dashboards/Downloads/Exactuals/**'

        for file_name in glob.glob(input_glob_pattern, recursive=True):
            if os.path.isfile(file_name) and file_name.endswith('.json'):
                with open(file_name, 'r', encoding='utf-8') as infile:
                    dashboard = json.loads(infile.read())
                    dashboard_id = dashboard.get('id')

                    if dashboard_id in known_collisions:
                        dashboard_name = dashboard.get('dashboardMetadata').get('name')
                        dashboard_owner = dashboard.get('dashboardMetadata').get('owner')
                        print(f'Known Collision: {dashboard_id}:{dashboard_name}:{dashboard_owner}')
                    else:
                        dashboard_id_list.append(dashboard_id)

        check_tenants(dashboard_id_list, tenant_dict)

    except FileNotFoundError:
        print('The directory name does not exist')


def load_tenants(env_name_list):
    tenant_dict = {}

    for env_name in env_name_list:
        _, env, token = environment.get_environment(env_name)

        endpoint = '/api/config/v1/dashboards'
        params = ''
        dashboards_json_list = dynatrace_api.get(env, token, endpoint, params)

        # count = 0
        tenant_list = []

        for dashboards_json in dashboards_json_list:
            inner_dashboards_json_list = dashboards_json.get('dashboards')
            for inner_dashboards_json in inner_dashboards_json_list:
                dashboard_id = inner_dashboards_json.get('id')
                # name = inner_dashboards_json.get('name')
                # owner = inner_dashboards_json.get('owner')
                tenant_list.append(dashboard_id)

        tenant_list = sorted(tenant_list)
        tenant_dict[env_name] = tenant_list

    return tenant_dict


def check_tenants(dashboard_list, tenant_dict):
    for key in tenant_dict.keys():
        tenant_list = tenant_dict[key]
        for dashboard_id in dashboard_list:
            if dashboard_id in tenant_list:
                print(f'Collision: {dashboard_id}')


if __name__ == '__main__':
    main()
