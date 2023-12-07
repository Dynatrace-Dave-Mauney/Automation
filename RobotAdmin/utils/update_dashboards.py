# import copy
import json
# import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def process_dashboards(env, token):
    count_total = 0
    count_updated = 0

    endpoint = '/api/config/v1/dashboards'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    dashboards_json_dict = r.json()
    dashboards_json_list = dashboards_json_dict.get('dashboards')

    for dashboards_json in dashboards_json_list:
        dashboard_id = dashboards_json.get('id')
        name = dashboards_json.get('name')
        owner = dashboards_json.get('owner')

        # new_name = name
        if '00000001-0000-0000-0000-' in dashboard_id or '00000001-0000-0000-0001-' in dashboard_id:
            if ' Service ' not in name and ' Synthetic ' not in name and name.endswith('SLOs'):
                if 'Browser' in name:
                    new_name = name.replace('Browser', 'Synthetic Browser')
                else:
                    new_name = name.replace('SLOs', 'Synthetic HTTP SLOs')

                print(name, new_name, dashboard_id, owner)
                dashboard = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{dashboard_id}', token)
                dashboard_metadata = dashboard.get('dashboardMetadata')
                dashboard_metadata['name'] = new_name

                payload = json.dumps(dashboard)
                r = dynatrace_api.put_object(f'{env}{endpoint}/{dashboard_id}', token, payload)
                if r.status_code != 204:
                    print(f'Bad status code: {r.status_code}')
                    exit(1)

                count_updated += 1

        count_total += 1

    print(f'Total Dashboards: {count_total}')
    print(f'Updated Dashboards: {count_updated}')


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    env_name_supplied = 'Personal'  # For Safety
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process_dashboards(env, token)


if __name__ == '__main__':
    main()
