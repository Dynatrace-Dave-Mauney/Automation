"""
Generate "Google Cloud Home Menu" Dashboard JSON.
"""

import json

directory_path = 'Templates/Overview'
dashboard_name = '00000000-dddd-bbbb-ffff-000000000130.json'


def main():
    # Use "list_gcp_dashboards.py" to generate this list and then tweak it per customer
    dashboard_links = [
        ('Google Cloud APIs', '#dashboard;id=7c39143d-6600-de20-538a-0574d01adb0f'),
        ('Google Cloud Datastore', '#dashboard;id=64ae63e6-e6bf-961d-077d-e1f86125bebf'),
        ('Google Cloud Filestore', '#dashboard;id=5c738a60-7ac5-2332-17bc-fdd1756ba757'),
        ('Google Cloud Function', '#dashboard;id=575bea5f-77e6-36b7-adf7-b0aa660c6812'),
        # ('Google Cloud HTTPs Load Balancing', '#dashboard;id=4186f854-64f1-0ffe-ffaf-e85e5442cc54'),
        ('Google Cloud InterConnect', '#dashboard;id=9d2eeccc-1204-425a-8eab-58eda2edea80'),
        ('Google Cloud Pub/Sub', '#dashboard;id=ac9373bd-b04c-5c86-8e77-6cdf58fa0aa5'),
        ('Google Cloud SQL', '#dashboard;id=51da2c17-a842-75ec-ac9c-9a954b564104'),
        ('Google Cloud Storage', '#dashboard;id=322b0e3f-eb4e-7ea3-c780-93035ac731e3'),
        # ('Google Cloud TCP Load Balancing', '#dashboard;id=3823cfb8-ae25-777a-1b00-58fcfc575b83'),
        ('Google Kubernetes Engine', '#dashboard;id=75fd0d04-6dcc-2d57-2823-4a4ca2b38504'),
        ('Google Virtual Machines', '#dashboard;id=1440fd00-07d1-ddbd-948f-3cf63b5100c7'),
    ]

    drilldown_title = '## {{.title}}  \\n'

    dashboard_template = '''{
  "metadata": {
    "configurationVersions": [
      6
    ],
    "clusterVersion": "1.261.134.20230302-084304"
  },
  "id": "00000000-dddd-bbbb-ffff-000000000130",
  "dashboardMetadata": {
    "name": "TEMPLATE: Google Cloud - Home",
    "shared": true,
    "owner": "nobody@example.com",
    "preset": false,
    "tilesNameSize": "small",
    "hasConsistentColors": true
  },
  "tiles": [
    {
      "name": "Markdown",
      "tileType": "MARKDOWN",
      "configured": true,
      "bounds": {
        "top": 0,
        "left": 0,
        "width": 494,
        "height": 608
      },
      "tileFilter": {},
      "isAutoRefreshDisabled": false,
      "markdown": "{{.dashboard_markdown}}"
    },
    {
      "name": "Markdown",
      "tileType": "MARKDOWN",
      "configured": true,
      "bounds": {
          "top": 0,
          "left": 1368,
          "width": 152,
          "height": 38
      },
      "tileFilter": {},
      "markdown": "#### [\u21e6 Overview](#dashboard;id=00000000-dddd-bbbb-ffff-000000000001)\\n![BackButton]()"
    }
  ]
}
    '''

    dashboard_markdown_title = drilldown_title.replace('{{.title}}', 'Dashboards')
    dashboard_markdown = dashboard_markdown_title
    for dashboard_link in dashboard_links:
        dashboard_key, dashboard_link = dashboard_link
        dashboard_markdown += f'  \\n[{dashboard_key}]({dashboard_link})'

    dashboard_template = dashboard_template.replace('{{.dashboard_markdown}}', dashboard_markdown)

    print(dashboard_template)

    write_json(directory_path, dashboard_name, json.loads(dashboard_template))

    aws_markdown_menu = '			"markdown": "'
    for dashboard_link in dashboard_links:
        dashboard_key, dashboard_link = dashboard_link
        aws_markdown_menu += f'  \\n[{dashboard_key}]({dashboard_link})'
    aws_markdown_menu += '"'

    filename = 'Templates/Overview/markdown_aws_menu.json'
    with open(filename, 'w') as file:
        file.write(aws_markdown_menu)


def write_json(path, filename, json_dict):
    # print('write_json(' + directory_path + ',' + filename + ',' + str(json_dict) + ')')
    file_path = f'{path}/{filename}'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(json_dict, indent=4, sort_keys=False))


if __name__ == '__main__':
    main()
