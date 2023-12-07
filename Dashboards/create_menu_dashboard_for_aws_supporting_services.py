import json

from Reuse import dynatrace_api
from Reuse import environment


menu_dashboard_template = {
  "metadata": {
    "configurationVersions": [
      6
    ],
    "clusterVersion": "1.253.206.20221104-095518"
  },
  "id": "00000000-dddd-bbbb-eeee-000000000000",
  "dashboardMetadata": {
    "name": "AWS Supporting Services (Dynatrace Owner)",
    "shared": True,
    "owner": "nobody@example.com.com",
    "preset": True,
    "hasConsistentColors": True
  },
  "tiles": [
    {
      "name": "Markdown",
      "tileType": "MARKDOWN",
      "configured": True,
      "bounds": {
        "top": 0,
        "left": 1368,
        "width": 152,
        "height": 38
      },
      "tileFilter": {},
      "markdown": "## [⇦](#dashboard;id=00000000-dddd-bbbb-ffff-000000000001)\n![BackButton]()"
    },
    {
      "name": "Markdown",
      "tileType": "MARKDOWN",
      "configured": True,
      "bounds": {
        "top": 0,
        "left": 0,
        "width": 304,
        "height": 570
      },
      "tileFilter": {},
      "markdown": "[1](#dashboard;id=00000000-dddd-bbbb-ffff-000000000001)\n\n\n[2](#dashboard;id=00000000-dddd-bbbb-ffff-000000000001)"
    }
  ]
}


def process(env, token):
    endpoint = '/api/config/v1/dashboards'
    dashboard_kvp_tuple_list = []
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    dashboard_json_list = r.json()

    for dashboard_json in dashboard_json_list.get('dashboards'):
        dashboard_id = dashboard_json.get('id')
        dashboard_name = dashboard_json.get('name')
        dashboard_owner = dashboard_json.get('owner')
        if "Dynatrace" in dashboard_owner and ('AWS' in dashboard_name or 'Amazon' in dashboard_name):
            dashboard_short_name = dashboard_name.replace('AWS ', '').replace('Amazon ', '')
            dashboard_kvp_tuple = (dashboard_short_name, dashboard_id)
            dashboard_kvp_tuple_list.append(dashboard_kvp_tuple)

    markdown_string = ''
    for dashboard_kvp_tuple in sorted(dashboard_kvp_tuple_list):
        dashboard_name = dashboard_kvp_tuple[0]
        dashboard_id = dashboard_kvp_tuple[1]
        markdown_string += '[' + dashboard_name + ']' + '(#dashboard;id=' + dashboard_id + ')  \n'

    dashboard = menu_dashboard_template
    dashboard['tiles'][1]['markdown'] = markdown_string
    dashboard_string = json.dumps(dashboard)
    put_dashboard(env, token, dashboard.get('id'), dashboard_string)
    print('Dashboard for ' + env + ':')
    print(env + '/#dashboard;id=' + dashboard.get('id'))


def put_dashboard(env, token, dashboard_id, payload):
    endpoint = '/api/config/v1/dashboards'
    dynatrace_api.put_object(f'{env}{endpoint}/{dashboard_id}', token, payload)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
