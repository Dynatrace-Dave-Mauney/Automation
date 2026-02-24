"""
Generate "Dynatrace Owner" Dashboard JSON.
"""

import json

directory_path = 'Templates/Overview'
dashboard_name = '00000000-dddd-bbbb-ffff-000000002000.json'


def main():
    dashboard_links = [
        ('Davis® health self-monitoring', '#dashboard;id=c15f39a8-7d74-4b97-af28-0b17a20dc711'),
        ('DPS Usage Details DEMO', '#dashboard;id=c4644591-ee8d-4bc2-8e50-d921344fe255'),
        # ('Kubernetes cluster overview', '#dashboard;id=6b38732e-8c5c-4b32-80a1-7053ec8f37e1'),
        # ('Kubernetes namespace resource quotas', '#dashboard;id=6b38732e-609c-44e2-b34d-0286717ecdab'),
        # ('Kubernetes persistent volume claims', '#dashboard;id=6b38732e-7d72-4200-be06-61672d0b3f65'),
        # ('Kubernetes workload overview', '#dashboard;id=6b38732e-d26b-45c7-b107-ed85e87ff288'),
        ('Metric & Dimension Usage + Rejections', '#dashboard;id=3b9c20e2-dc58-4a91-8dcb-f6217dc869ac'),
        ('Monitored Entities Health Check', '#dashboard;id=9172cf73-afd4-49cf-81f7-7dd2160a5405'),
        ('NetApp OnTap Overview', '#dashboard;id=051f3484-3165-caf5-7a9d-caeae85b44f6'),
        ('Pure Storage FlashArray Entities Overview', '#dashboard;id=bf6c71d8-0758-504c-787c-654c8d229250'),
        ('Pure Storage FlashArray Fleet Overview (OpenMetrics)', '#dashboard;id=affc78a0-10fc-8107-5e90-3446f717fa47'),
        # ('OneAgent Traces - Adaptive traffic management DPS (deprecated)', '#dashboard;id=f481dbe9-0853-465b-9b69-e31c403c6b84'),
        # ('Real User Monitoring', '#dashboard;id=c704bd72-92e9-452a-b40e-73e6f4df9f08'),
        # ('Synthetic Monitoring', '#dashboard;id=b6fc0160-9332-454f-a7bc-7217b2ae540c'),
        ('Tagging worker Dashboard (Deprecated) – Use Monitored Entities Health Check', '#dashboard;id=25bdae36-8e74-471d-a314-ac750b4ef190'),
        ('VMware Extension Overview', '#dashboard;id=a5f3de52-5722-eec6-cae4-f55ba4a7d7a2'),
        ('VMware Capacity Overview', '#dashboard;id=836ff169-081c-e2b3-e1b4-8249ff890b71'),
    ]
    # dashboard_links = [
    #     ('Active Directory Overview', '#dashboard;id=0de4b077-8eac-5074-1ce9-b5681a9e27b3'),
    #     ('Certificate Monitor Extension Overview', '#dashboard;id=30a81bcc-fde9-cf93-adb8-6f2d878dd1ed'),
    #     ('Cisco SNMP device', '#dashboard;id=8fe09b9a-1c3d-0576-7dfc-898752ffc183'),
    #     ('DPS Usage Details DEMO', '#dashboard;id=c4644591-ee8d-4bc2-8e50-d921344fe255'),
    #     ('Davis® health self-monitoring', '#dashboard;id=c15f39a8-7d74-4b97-af28-0b17a20dc711'),
    #     ('Kubernetes Monitoring Statistics', '#dashboard;id=68d2b0d3-2258-5443-0804-0d72a3a1cf1d'),
    #     ('Kubernetes cluster overview', '#dashboard;id=6b38732e-8c5c-4b32-80a1-7053ec8f37e1'),
    #     ('Kubernetes namespace resource quotas', '#dashboard;id=6b38732e-609c-44e2-b34d-0286717ecdab'),
    #     ('Kubernetes persistent volume claims', '#dashboard;id=6b38732e-7d72-4200-be06-61672d0b3f65'),
    #     ('Kubernetes workload overview', '#dashboard;id=6b38732e-d26b-45c7-b107-ed85e87ff288'),
    #     ('Metric & Dimension Usage + Rejections', '#dashboard;id=3b9c20e2-dc58-4a91-8dcb-f6217dc869ac'),
    #     # ('Mulesoft Cloudhub Overview', '#dashboard;id=9b386608-d386-a9c0-163f-aa67d28208ec'),
    #     # ('Mulesoft MQ Overview', '#dashboard;id=0c2cebfa-91ee-0a71-216a-ebc05117a026'),
    #     # ('MySQL Overview', '#dashboard;id=b0af7ee0-f4e8-a5c6-7289-0a6568cf30f8'),
    #     ('NetApp OnTap Overview', '#dashboard;id=051f3484-3165-caf5-7a9d-caeae85b44f6'),
    #     ('Network infrastructure performance (Generic SNMP devices)', '#dashboard;id=e3dc6c8c-d4da-4ead-56ca-40beef4d47ec'),
    #     ('OneAgent Traces - Adaptive traffic management DPS', '#dashboard;id=358f9385-cc60-43f3-aa98-82d80e403e88'),
    #     # ('Postgres Overview ', '#dashboard;id=c5344e23-a6aa-3b42-e205-d4b1c8749a2e'),
    #     ('Real User Monitoring', '#dashboard;id=c704bd72-92e9-452a-b40e-73e6f4df9f08'),
    #     # ('Remote Unix Overview', '#dashboard;id=4c2a5361-1fe4-6d19-e590-3e1e7569db6a'),
    #     ('SNMP Auto-discovery', '#dashboard;id=25ea4d62-c534-6dd0-2617-dfbf89a216aa'),
    #     # ('SNMP traps', '#dashboard;id=639697bc-e9ae-d85e-049f-a435c63604ae'),
    #     ('Synthetic Monitoring', '#dashboard;id=b6fc0160-9332-454f-a7bc-7217b2ae540c'),
    #     ('Tagging worker Dashboard', '#dashboard;id=0adb4db7-2172-4f6b-9c41-2bd9c18e52d2'),
    #     ('VMware Capacity Overview', '#dashboard;id=836ff169-081c-e2b3-e1b4-8249ff890b71'),
    #     ('VMware Extension Overview', '#dashboard;id=a5f3de52-5722-eec6-cae4-f55ba4a7d7a2'),    ]
    #
    drilldown_title = '## {{.title}}  \\n'

    dashboard_template = '''{
  "metadata": {
    "configurationVersions": [
      6
    ],
    "clusterVersion": "1.261.134.20230302-084304"
  },
  "id": "00000000-dddd-bbbb-ffff-000000002000",
  "dashboardMetadata": {
    "name": "TEMPLATE: Dynatrace-owned Dashboards",
    "shared": true,
    "preset": false,
    "owner": "nobody@example.com",
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
        "width": 1368,
        "height": 1368
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
          "height": 152
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


def write_json(path, filename, json_dict):
    # print('write_json(' + path + ',' + filename + ',' + str(json_dict) + ')')
    file_path = f'{path}/{filename}'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(json_dict, indent=4, sort_keys=False))


if __name__ == '__main__':
    main()
