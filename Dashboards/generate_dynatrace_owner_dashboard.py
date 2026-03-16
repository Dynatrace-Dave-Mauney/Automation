"""
Generate "Dynatrace Owner" Dashboard JSON.
"""

import json

directory_path = 'Templates/Overview'
dashboard_name = '00000000-dddd-bbbb-ffff-000000002000.json'


def main():
    dashboard_links = [
        ('Active Directory Overview', '#dashboard;id=d0b9d314-87a5-c38f-0501-6f59e3931770'),
        ('Cisco Device Overview', '#dashboard;id=98a3eb9a-6d47-a991-d2cc-d0c7f4c338b4'),
        ('Cisco UCS Extension Overview - C-Series', '#dashboard;id=0cc9390b-e2d7-5e7b-020d-de5c9b9e4caa'),
        ('Cisco UCS Extension Overview - M-Series', '#dashboard;id=b0e82781-0fc9-7e5e-e92b-95f68296d083'),
        ('Citrix ADC (Netscaler) - Overview', '#dashboard;id=f4917e90-45ac-3fff-0ac7-e3d021be3df7'),
        ('Citrix SDX (Netscaler) - Overview', '#dashboard;id=7cdec109-b581-4799-2665-f4556848377a'),
        ('Citrix Virtual Apps and Desktops Overview', '#dashboard;id=eb3bf8d8-8266-1e96-41c4-e4b1cb32457a'),
        ('DPS Usage Details DEMO', '#dashboard;id=c4644591-ee8d-4bc2-8e50-d921344fe255'),
        ('Davis® health self-monitoring', '#dashboard;id=c15f39a8-7d74-4b97-af28-0b17a20dc711'),
        ('HP iLO Overview', '#dashboard;id=93bd59c3-614e-88af-ce03-849e83e1d939'),
        ('IBM i Overview', '#dashboard;id=e920c93e-5d80-a466-aaa5-6b495c429933'),
        ('Infoblox DDI Extension Overview', '#dashboard;id=e608a54e-518b-4f63-9cbe-fe68b6535a6d'),
        # ('Kubernetes cluster overview', '#dashboard;id=6b38732e-8c5c-4b32-80a1-7053ec8f37e1'),
        # ('Kubernetes namespace resource quotas', '#dashboard;id=6b38732e-609c-44e2-b34d-0286717ecdab'),
        # ('Kubernetes persistent volume claims', '#dashboard;id=6b38732e-7d72-4200-be06-61672d0b3f65'),
        # ('Kubernetes workload overview', '#dashboard;id=6b38732e-d26b-45c7-b107-ed85e87ff288'),
        ('Metric usage and rejection self-monitoring', '#dashboard;id=3b9c20e2-dc58-4a91-8dcb-f6217dc869ac'),
        ('Monitored entities health self-monitoring', '#dashboard;id=60f5492a-10af-41c0-b56f-efd08cd9984b'),
        ('NetApp OnTap Overview', '#dashboard;id=051f3484-3165-caf5-7a9d-caeae85b44f6'),
        ('Nutanix Overview', '#dashboard;id=761de425-e905-6b68-d32a-5d3948ac82f3'),
        ('OCI Autonomous Database', '#dashboard;id=30c7fe74-36fd-e42a-afff-e2477207c3aa'),
        ('OCI Core Services', '#dashboard;id=ce1690f2-d6ca-8055-b3d7-1b0231f28b56'),
        ('OneAgent Traces - Adaptive traffic management DPS (deprecated)',
         '#dashboard;id=f481dbe9-0853-465b-9b69-e31c403c6b84'),
        ('Oracle Database Overview', '#dashboard;id=28130395-2cf2-d9e3-b19b-ebfb64862f7e'),
        ('Pure Storage FlashArray Entities Overview', '#dashboard;id=bf6c71d8-0758-504c-787c-654c8d229250'),
        ('Pure Storage FlashArray Fleet Overview (OpenMetrics)', '#dashboard;id=affc78a0-10fc-8107-5e90-3446f717fa47'),
        ('Real User Monitoring', '#dashboard;id=c704bd72-92e9-452a-b40e-73e6f4df9f08'),
        ('SNMP Auto-discovery', '#dashboard;id=25ea4d62-c534-6dd0-2617-dfbf89a216aa'),
        ('SQL Server (Local)', '#dashboard;id=dde3114c-d41b-a6e9-87d3-414257c25377'),
        ('SQL Server - Python WMI', '#dashboard;id=8f1d1f78-f411-77c3-3503-f875d27dee0a'),
        ('SQL Server Overview', '#dashboard;id=3fcc4524-520c-b971-fb56-7db04944d0cc'),
        ('Synthetic Monitoring', '#dashboard;id=b6fc0160-9332-454f-a7bc-7217b2ae540c'),
        ('VMware Capacity Overview', '#dashboard;id=836ff169-081c-e2b3-e1b4-8249ff890b71'),
        ('VMware Extension Overview', '#dashboard;id=a5f3de52-5722-eec6-cae4-f55ba4a7d7a2'),
        ('Veritas NetBackup - Overview', '#dashboard;id=66b997e9-0c94-e667-1d47-a1e99e95d6c3'),
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

    # print(dashboard_template)

    write_json(directory_path, dashboard_name, json.loads(dashboard_template))


def write_json(path, filename, json_dict):
    # print('write_json(' + path + ',' + filename + ',' + str(json_dict) + ')')
    file_path = f'{path}/{filename}'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(json_dict, indent=4, sort_keys=False))
        print(f'File written: {path}/{filename}')


if __name__ == '__main__':
    main()
