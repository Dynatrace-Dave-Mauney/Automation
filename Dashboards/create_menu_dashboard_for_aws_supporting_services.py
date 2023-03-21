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


def index_dashboards(env, token):
    endpoint = '/api/config/v1/dashboards'
    dashboard_kvp_tuple_list = []
    res = json.loads(dynatrace_api.get_object_list(env, token, endpoint).text)
    for entry in res['dashboards']:
        dashboard_id = entry.get('id')
        dashboard_name = entry.get('name')
        dashboard_owner = entry.get('owner')
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
    dynatrace_api.put(env, token, endpoint, dashboard_id, payload)


def main():
    # env_name, env, tenant, token = get_environment('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, env, tenant, token = get_environment('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    env_name, env, token = environment.get_environment('Dev')
    index_dashboards(env, token)


if __name__ == '__main__':
    main()

