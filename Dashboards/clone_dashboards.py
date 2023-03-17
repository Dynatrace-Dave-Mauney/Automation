"""

For safety, a clone will only be done for a specific dashboard.

Remove the if statement to clone all dashboards.

"""

import json


from Reuse import dynatrace_api
from Reuse import environment


def process(source_env, source_token, target_env, target_token):
    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboard_json_list = dynatrace_api.get(source_env, source_token, endpoint, params)
    for dashboard_json in dashboard_json_list:
        inner_dashboard_json_list = dashboard_json.get('dashboards')
        for inner_dashboard_json in inner_dashboard_json_list:
            dashboard_id = inner_dashboard_json.get('id')
            dashboard_name = inner_dashboard_json.get('name')
            print(dashboard_id)
            if dashboard_id == '00000000-0000-0000-0000-000000000000':
                dashboard = dynatrace_api.get_by_object_id(source_env, source_token, endpoint, dashboard_id)
                # To change the owner
                # owner = dashboard.get('dashboardMetadata').get('owner')
                # dashboard['dashboardMetadata']['owner'] = 'nobody@example.com'
                # You may want to use POST if cloning in the same tenant.
                # But generally, PUT is preferred, when "fixed ids' are used.
                # response = dynatrace_api.post(target_env, target_token, endpoint, json.dumps(dashboard, indent=4, sort_keys=False))
                response = dynatrace_api.put(target_env, target_token, endpoint, dashboard_id, json.dumps(dashboard, indent=4, sort_keys=False))
                if response.status_code == 204:
                    print(f'Cloned {dashboard_name} ({dashboard_id}) from {source_env} to {target_env} with same name and id as an UPDATE')
                else:
                    new_dashboard_id = json.loads(response.text).get('id')
                    print(f'Cloned {dashboard_name} ({dashboard_id}) from {source_env} to {target_env} with same name and id of {new_dashboard_id}')


def main():
    source_env_name = 'Personal'
    target_env_name = 'FreeTrial1'
    env_name, source_env, source_token = environment.get_environment(source_env_name)
    env_name, target_env, target_token = environment.get_environment(target_env_name)
    process(source_env, source_token, target_env, target_token)


if __name__ == '__main__':
    main()
