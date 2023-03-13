"""
Generate "AWS Home Menu" Dashboard JSON.
"""

import json

# directory_path = '../../Dashboards/Templates/Overview'
directory_path = 'Templates/Overview'
dashboard_name = '00000000-dddd-bbbb-ffff-000000001000.json'

def main():
	dashboard_links = [
		('AWS ALB', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001023'),
		('AWS API Gateway', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001008'),
		('AWS CloudWatch Logs', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001010'),
		('AWS Cloudfront', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001009'),
		('AWS Connect', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001011'),
		('AWS Connect Details', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001020'),
		('AWS DynamoDB', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001002'),
		('AWS DynamoDB Accelerator (DAX)', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001022'),
		('AWS EBS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001003'),
		('AWS EC2', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001004'),
		('AWS EC2 Auto Scaling', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001021'),
		('AWS ECS ContainerInsights', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001013'),
		('AWS ECS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001012'),
		('AWS ES', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001024'),
		('AWS Kinesis Data Streams', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001019'),
		('AWS Lambda Functions', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001005'),
		('AWS Lex', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001014'),
		('AWS NAT Gateways', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001015'),
		('AWS NLB', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001006'),
		('AWS RDS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001007'),
		('AWS Route 53', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001016'),
		('AWS Route 53 Resolver', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001017'),
		('AWS Site-to-Site VPN', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001018'),
		('AWS SQS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001025'),
	]

	view_links = [
		('AWS', '#awses'),
		('AWS Settings', '#settings/awsmonitoring'),
	]

	drilldown_title = '## {{.title}}  \\n'

	dashboard_template = '''{
  "metadata": {
    "configurationVersions": [
      6
    ],
    "clusterVersion": "1.261.134.20230302-084304"
  },
  "id": "00000000-dddd-bbbb-ffff-000000001000",
  "dashboardMetadata": {
    "name": "TEMPLATE: AWS Home",
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



def write_json(directory_path, filename, json_dict):
	# print('write_json(' + directory_path + ',' + filename + ',' + str(json_dict) + ')')
	file_path = f'{directory_path}/{filename}'
	with open(file_path, 'w', encoding='utf-8') as file:
		file.write(json.dumps(json_dict, indent=4, sort_keys=False))


if __name__ == '__main__':
	main()
