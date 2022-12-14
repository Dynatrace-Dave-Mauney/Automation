import json
import os
import requests
import ssl

dashboard_index_template = {
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
    dashboard_kvp_tuple_list = []
    try:
        headers = {'Authorization': 'Api-Token ' + token}
        r = requests.get(env + '/api/config/v1/dashboards', headers=headers)
        # print("%s save list: %d" % ('dashboards', r.status_code))
        # print(r.content)
        res = r.json()
        for entry in res['dashboards']:
            dashboard_id = entry.get('id')
            dashboard_name = entry.get('name')
            dashboard_owner = entry.get('owner')
            if "Dynatrace" in dashboard_owner and ('AWS' in dashboard_name or 'Amazon' in dashboard_name):
                dashboard_short_name = dashboard_name.replace('AWS ', '').replace('Amazon ', '')
                # print(dashboard_short_name, dashboard_id)
                dashboard_kvp_tuple = (dashboard_short_name, dashboard_id)
                dashboard_kvp_tuple_list.append(dashboard_kvp_tuple)
        # print(sorted(dashboard_kvp_tuple_list))

        markdown_string = ''
        for dashboard_kvp_tuple in sorted(dashboard_kvp_tuple_list):
            dashboard_name = dashboard_kvp_tuple[0]
            # print(dashboard_name)
            dashboard_id = dashboard_kvp_tuple[1]
            markdown_string += '[' + dashboard_name + ']' + '(#dashboard;id=' + dashboard_id + ')  \n'

        # print(markdown_string)

        dashboard = dashboard_index_template
        dashboard['tiles'][1]['markdown'] = markdown_string
        dashboard_string = json.dumps(dashboard)
        put_dashboard(env, token, dashboard.get('id'), dashboard_string)
        print('Dashboard for ' + env + ':')
        print(env + '/#dashboard;id=' + dashboard.get('id'))

    except ssl.SSLError:
        print("SSL Error")


def put_dashboard(env, token, dashboard_id, payload):
    url = env + '/api/config/v1/dashboards/' + dashboard_id
    print('PUT: ' + url)
    try:
        r = requests.put(url, payload.encode('utf-8'),
                         headers={'Authorization': 'Api-Token ' + token,
                                  'Content-Type': 'application/json; charset=utf-8'})
        # If you need to bypass certificate checks on managed and are ok with the risk:
        # r = requests.put(url, payload, headers=HEADERS, verify=False)
        print('Status Code: %d' % r.status_code)
        print('Reason: %s' % r.reason)
        if len(r.text) > 0:
            print(r.text)
        if r.status_code not in [200, 201, 204]:
            exit()
    except ssl.SSLError:
        print('SSL Error')


def main():
    # env_name, env, tenant, token = get_environment('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, env, tenant, token = get_environment('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    env_name, env, tenant, token = get_environment('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')

    print('Environment:     ' + env_name)
    print('Environment URL: ' + env)

    index_dashboards(env, token)


def get_environment(env_name, tenant_key, token_key):
    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    return env_name, env, tenant, token


if __name__ == '__main__':
    main()

