"""
Generate "Dynatrace Owner" Dashboard JSON.
"""

import json

directory_path = 'Templates/Overview'
dashboard_name = '00000000-dddd-bbbb-ffff-000000002000.json'


def main():
    dashboard_links = [
        ('AWS API Usage', '#dashboard;id=bbfc992a-da6d-45ee-be47-df6b217ad765'),
        ('AWS Billing', '#dashboard;id=c12daf08-2a86-4efa-b713-9175b5b4017b'),
        # ('AWS CodeBuild', '#dashboard;id=1736b64b-b118-44f6-b8f6-2fc359fefda6'),
        # ('AWS DMS', '#dashboard;id=8e25b445-26ea-4812-b805-88df626afbd6'),
        # ('AWS Direct Connect', '#dashboard;id=b17d6b42-27cd-4dd4-9783-65b302179e79'),
        # ('AWS Step Functions', '#dashboard;id=4387929f-68b1-4d71-a2b1-4e601856ef09'),
        # ('AWS Storage Gateway', '#dashboard;id=09372eaa-3347-4959-a049-3c993fe3420f'),
        # ('AWS Systems Manager - Run Command', '#dashboard;id=2907d217-d5ef-480e-9b44-c7b66a8028a8'),
        ('AWS Trusted Advisor', '#dashboard;id=a55d8a88-0841-43fd-be97-68f4b877f97b'),
        ('AWS WAFV2', '#dashboard;id=ee0dd7a8-15ca-4b94-af6e-0a37f8361f1a'),
        ('Active Directory Overview', '#dashboard;id=0de4b077-8eac-5074-1ce9-b5681a9e27b3'),
        ('Amazon ActiveMQ', '#dashboard;id=492fa8c2-427e-430c-8856-7bf32d6be64d'),
        # ('Amazon Athena', '#dashboard;id=99c6d8f1-a355-46bd-9f6a-f2a85f30efcf'),
        ('Amazon CloudWatch Logs', '#dashboard;id=b8e6ea06-70c3-4bfa-8fef-d3c68c7a7c67'),
        ('Amazon Connect', '#dashboard;id=c82a7373-c954-4b32-a374-fdb0be89de92'),
        # ('Amazon DynamoDB Accelerator (DAX)', '#dashboard;id=f388375b-a36e-4d18-ba47-0187f43c2446'),
        # ('Amazon EC2 Auto Scaling', '#dashboard;id=7906dd7c-d5b0-4cf5-be45-8228d45d349e'),
        ('Amazon ECS Container Insights', '#dashboard;id=7645a470-292c-486a-b9cc-b60be94d52f5'),
        # ('Amazon Elastic Kubernetes Service (EKS)', '#dashboard;id=74e63e2e-a084-482c-a87d-d96e87192c23'),
        ('Amazon EventBridge', '#dashboard;id=0c111823-b2c6-4ee6-98a1-5acba91c8579'),
        # ('Amazon Lex', '#dashboard;id=f3d22b91-e261-4251-be93-a0636f7fc634'),
        ('Amazon MSK (Kafka)', '#dashboard;id=0b4a7075-9107-4e01-aaa4-2cca590470b1'),
        # ('Amazon RabbitMQ', '#dashboard;id=4ae9a988-46b1-4d61-81c8-ea58859b9c23'),
        ('Amazon Route 53', '#dashboard;id=454c4321-e972-401d-847d-53c421c76fcb'),
        ('Amazon Textract', '#dashboard;id=3bd5a934-bd30-4513-8097-04be12ba4b99'),
        # ('Amazon Translate', '#dashboard;id=6096e827-de96-4302-aaf6-6327a3bfdf86'),
        # ('Apache ActiveMQ Overview', '#dashboard;id=f853dd8e-2b47-addc-040a-90bae4c8e703'),
        ('Citrix ADC (Netscaler) - Overview', '#dashboard;id=f4917e90-45ac-3fff-0ac7-e3d021be3df7'),
        # ('Citrix Virtual Apps and Desktops Overview', '#dashboard;id=eb3bf8d8-8266-1e96-41c4-e4b1cb32457a'),
        ('DPS Usage Details DEMO', '#dashboard;id=c4644591-ee8d-4bc2-8e50-d921344fe255'),
        ('Davis® health self-monitoring', '#dashboard;id=c15f39a8-7d74-4b97-af28-0b17a20dc711'),
        ('Extensions Health', '#dashboard;id=c6f43fb9-5abd-de75-871d-6c700489e89f'),
        ('Extensions usage', '#dashboard;id=3780e69a-430e-10dd-dd8b-6abc9bd35e82'),
        ('F5 BIG-IP GTM Overview', '#dashboard;id=943ebb6a-444a-6760-fbf2-63c27a7676c1'),
        ('F5 BIG-IP LTM Overview', '#dashboard;id=0e5516cf-699c-d31d-6d1d-985dfc791580'),
        ('F5 BIGIP LTM Status', '#dashboard;id=1a4f0f04-cb4d-c819-e3bc-297eb95dcf23'),
        ('Generic Palo Alto', '#dashboard;id=ab163c60-07f5-7e82-40d5-35cd6a8be991'),
        ('GitHub Enterprise - Overview', '#dashboard;id=11d6b820-45b2-1410-89e6-c6a1958d5b74'),
        ('IBM MQ Monitoring Overview', '#dashboard;id=381c67c7-226b-4e00-5a2e-64bcdf4cf31b'),
        ('IIS Overview', '#dashboard;id=34da3850-67a4-550b-86b7-7c4baa4f8419'),
        ('Kafka Extension Overview', '#dashboard;id=a1ffbded-55b5-2725-4647-4ad2bf028dcd'),
        ('Kubernetes cluster overview', '#dashboard;id=6b38732e-8c5c-4b32-80a1-7053ec8f37e1'),
        ('Kubernetes namespace resource quotas', '#dashboard;id=6b38732e-609c-44e2-b34d-0286717ecdab'),
        ('Kubernetes persistent volume claims', '#dashboard;id=6b38732e-7d72-4200-be06-61672d0b3f65'),
        ('Kubernetes workload overview', '#dashboard;id=6b38732e-d26b-45c7-b107-ed85e87ff288'),
        ('MS Exchange 2013', '#dashboard;id=c1332960-ee42-f734-6608-f447c2279bba'),
        ('MS Exchange', '#dashboard;id=33026358-80b4-6cdf-5123-8af95dec3c77'),
        ('Metric usage and rejection self-monitoring', '#dashboard;id=3b9c20e2-dc58-4a91-8dcb-f6217dc869ac'),
        ('Monitored entities health self-monitoring', '#dashboard;id=60f5492a-10af-41c0-b56f-efd08cd9984b'),
        ('OneAgent Traces - Adaptive traffic management DPS (deprecated)', '#dashboard;id=f481dbe9-0853-465b-9b69-e31c403c6b84'),
        ('Oracle Database Overview', '#dashboard;id=28130395-2cf2-d9e3-b19b-ebfb64862f7e'),
        ('Postgres Overview ', '#dashboard;id=c5344e23-a6aa-3b42-e205-d4b1c8749a2e'),
        ('Real User Monitoring', '#dashboard;id=c704bd72-92e9-452a-b40e-73e6f4df9f08'),
        ('Synthetic Monitoring', '#dashboard;id=b6fc0160-9332-454f-a7bc-7217b2ae540c'),
    ]

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
