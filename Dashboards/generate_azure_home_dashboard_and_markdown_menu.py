"""
Generate "Azure Home Menu" Dashboard JSON.
"""

import json

directory_path = 'Templates/Overview'
dashboard_name = '00000000-dddd-bbbb-ffff-000000000110.json'


def main():
    # Use "list_azure_dashboards.py" to generate this list and then tweak it per customer
    dashboard_links = [
        ('Azure Monitoring Overview', '#dashboard;id=00000000-dddd-bbbb-ffff-000000000111'),
        ('Azure App Configuration', '#dashboard;id=4e563f70-ee02-474c-8823-35771c14a441'),
        ('Azure App Service Plan', '#dashboard;id=bf71f71f-d8ee-4145-b054-3526bb194141'),
        ('Azure Application Insights', '#dashboard;id=ad31b4e2-2e1b-41b7-82a2-5973ed5df6d1'),
        ('Azure Cognitive Services', '#dashboard;id=e384d4b9-5fd8-4772-aa1c-6b027cea2b27'),
        ('Azure Container Registries', '#dashboard;id=3de97c38-52a5-4979-8b44-791fb8f24c0b'),
        # ('Azure Event Hubs', '#dashboard;id=dd732f71-d91e-4f71-8ffa-c80b601b8475'),
        ('Azure ExpressRoute Circuit', '#dashboard;id=c2e6085c-8574-499d-8350-c825c9a83638'),
        # ('Azure Firewall', '#dashboard;id=65bfc2c1-9081-40c8-ab00-e10e1f10ef42'),
        # ('Azure Function App Deployment Slot', '#dashboard;id=c7ef230f-9a65-4469-b1c9-dd6047796ef3'),
        # ('Azure Gateway Metrics', '#dashboard;id=5428d2a7-780e-4bf7-ab54-e4e33f183a94'),
        ('Azure Ingress Networking', '#dashboard;id=d43d3123-728e-44f2-8296-f0411b4dd78c'),
        ('Azure Key Vault', '#dashboard;id=ad391b46-4ebc-441c-b44f-7c5e60220eb2'),
        ('Azure Kubernetes Service (AKS)', '#dashboard;id=fedc536d-fe04-4804-b9e1-5c07e18d71dd'),
        ('Azure Logic Apps', '#dashboard;id=c6808b60-24c0-447f-8498-4cdc507c43a4'),
        ('Azure Monitoring DocBox', '#dashboard;id=256ef22a-3cc6-4fc4-8065-9b0797440403'),
        ('Azure Network Interface', '#dashboard;id=e61187ef-bc0d-4eae-9a0a-9ebd4dc3bdb9'),
        ('Azure OpenAI', '#dashboard;id=94aac938-e42a-4ab5-a97a-202366234e87'),
        ('Azure Public IPs', '#dashboard;id=604e2a47-986d-44be-8edc-b3e7f406e089'),
        # ('Azure SQL Database Hyperscale', '#dashboard;id=24981f56-f02c-4f36-a700-0d326b8db374'),
        ('Azure SQL managed instances', '#dashboard;id=0b009a0f-fcb3-4dc3-afa2-54921416189e'),
        ('Azure Search', '#dashboard;id=2b495fd6-9683-4833-97b7-8746d1bb8e7f'),
        ('Azure SignalR Services', '#dashboard;id=1798548b-0176-4369-8f1d-fe94e988ea48'),
        # ('Azure Storage Account', '#dashboard;id=591dc04c-7835-416c-9f78-076c263db028'),
        ('Azure Synapse Workspace', '#dashboard;id=7f846065-4c35-4bb3-b352-67eff18c228c'),
        # ('Azure Time Series Insights Environment', '#dashboard;id=f2fc01b9-d485-43a8-b07b-5508e4bfcd46'),
        # ('Azure Time Series Insights Event Sources', '#dashboard;id=b0a3aaf9-2eaf-4057-9381-fcde0d9a77cb'),
        # ('Azure Virtual Machine Classic', '#dashboard;id=f518c522-e763-446f-b85a-fe627a96fde1'),
        # ('Azure Virtual Network Gateway', '#dashboard;id=55da70ff-e4f6-4f6f-8041-76f6ee5e7bbd'),
    ]

    view_links = [
        ('Azure', '#azures'),
        ('Azure Settings', '#settings/azuremonitoring'),
    ]

    drilldown_title = '## {{.title}}  \\n'

    dashboard_template = '''{
  "metadata": {
    "configurationVersions": [
      6
    ],
    "clusterVersion": "1.261.134.20230302-084304"
  },
  "id": "00000000-dddd-bbbb-ffff-000000000110",
  "dashboardMetadata": {
    "name": "TEMPLATE: Azure - Home",
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
        "left": 494,
        "width": 494,
        "height": 608
      },
      "tileFilter": {},
      "isAutoRefreshDisabled": false,
      "markdown": "{{.view_markdown}}"
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

    view_markdown_title = drilldown_title.replace('{{.title}}', 'Views')
    view_markdown = view_markdown_title
    for view_link in view_links:
        view_key, view_link = view_link
        view_markdown += f'  \\n[{view_key}]({view_link})'

    dashboard_template = dashboard_template.replace('{{.dashboard_markdown}}', dashboard_markdown)
    dashboard_template = dashboard_template.replace('{{.view_markdown}}', view_markdown)

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
