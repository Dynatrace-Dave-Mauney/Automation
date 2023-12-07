"""

For safety, a clone will only be done for a specific dashboard.

Remove the if statement to clone all dashboards.

"""

import json


from Reuse import dynatrace_api
from Reuse import environment


def process(source_env, source_token, target_env, target_token):
    endpoint = '/api/config/v1/dashboards'
    dashboard_json_list = dynatrace_api.get_json_list_with_pagination(f'{source_env}{endpoint}', source_token)
    for dashboard_json in dashboard_json_list:
        inner_dashboard_json_list = dashboard_json.get('dashboards')
        for inner_dashboard_json in inner_dashboard_json_list:
            dashboard_id = inner_dashboard_json.get('id')
            dashboard_name = inner_dashboard_json.get('name')
            print(dashboard_id)
            # if dashboard_id == '00000000-0000-0000-0000-000000000000':
            if dashboard_id == '0b9e7c0b-0797-429f-ace0-e8b666520b73':
                r = dynatrace_api.get_without_pagination(f'{source_env}{endpoint}/{dashboard_id}', source_token)
                dashboard = r.json()
                # To change the owner
                # owner = dashboard.get('dashboardMetadata').get('owner')
                # dashboard['dashboardMetadata']['owner'] = 'nobody@example.com'
                # You may want to use POST if cloning in the same tenant.
                # But generally, PUT is preferred, when "fixed ids' are used.
                response = dynatrace_api.put_object(f'{target_env}{endpoint}/{dashboard_id}', target_token, json.dumps(dashboard, indent=4, sort_keys=False))
                if response.status_code == 204:
                    print(f'Cloned {dashboard_name} ({dashboard_id}) from {source_env} to {target_env} with same name and id as an UPDATE')
                else:
                    new_dashboard_id = json.loads(response.text).get('id')
                    print(f'Cloned {dashboard_name} ({dashboard_id}) from {source_env} to {target_env} with same name and id of {new_dashboard_id}')


def main():
    source_env_name = 'Demo'
    target_env_name = 'Personal'
    env_name, source_env, source_token = environment.get_environment(source_env_name)
    env_name, target_env, target_token = environment.get_environment(target_env_name)
    process(source_env, source_token, target_env, target_token)


if __name__ == '__main__':
    main()
