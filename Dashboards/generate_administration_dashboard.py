"""
Generate "Administration Menu" Dashboard JSON.
"""

import json

directory_path = 'Templates/Overview'
dashboard_name = '00000000-dddd-bbbb-ffff-000000000800-v2.json'

def main():
	dashboard_links = [
		('Dynatrace Usage and Billing', '#dashboard;id=00000000-dddd-bbbb-ffff-000000000812'),
		('DPS Usage Details', '#dashboard;id=00000000-dddd-bbbb-ffff-000000000811'),
		('Licensing Overview', '#dashboard;id=00000000-dddd-bbbb-ffff-000000000801'),
		('Billing', '#dashboard;id=00000000-dddd-bbbb-ffff-000000000805'),
		('Host Health Breakdown', '#dashboard;id=00000000-dddd-bbbb-ffff-000000000807'),
		('Problem Notifications Health Overview', '#dashboard;id=00000000-dddd-bbbb-ffff-000000000809'),
		('3rd Party XHR Detection', '#dashboard;id=00000000-dddd-bbbb-ffff-000000000808'),
		('Dynatrace Self-Monitoring', '#dashboard;id=00000000-dddd-bbbb-ffff-000000000806'),
		('OneAgent Health Overview', '#dashboard;id=00000000-dddd-bbbb-ffff-000000000810'),
	]

	view_links = [
		('Access Tokens', '/ui/access-tokens'),
		('Consumption', '/ui/consumption/ddu/overview'),
		('Credential Vault', '#credentialvault'),
		('Custom Devices', '#newcustomdevices'),
		('Deploy Dynatrace', '#deploy'),
		('Deployment Status', '/ui/deploymentstatus/oneagents'),
		('Dynatrace Hub', '/ui/hub'),
		('Extensions', '/ui/hub'),
		('Synthetic', '#monitors'),
		('System Notifications', '/ui/system-notifications'),
	]

	setting_links = [
		('Settings', '#settings'),
		# 800-v2 has no AWS
		# ('AWS', '#settings/awsmonitoring'),
		('Application Detection', '/ui/settings/builtin:rum.web.app-detection'),
		('Automatically applied tags', '/ui/settings/builtin:tags.auto-tagging'),
		('Calculated Service Metrics', '#settings/serviceMetrics'),
		('Custom Service Detection', '#settings/newcustomservices'),
		('Deep Monitoring', '#settings/deepmonitoring'),
		('Maintenance Windows', '/ui/settings/builtin:alerting.maintenance-window'),
		('Management Zones', '/ui/settings/builtin:management-zones'),
		('Manually applied tags', '#settings/taggingoverview/tagging'),
		('Metric Events', '/ui/settings/builtin:anomaly-detection.metric-events'),
		('OneAgent Features', '/ui/settings/builtin:oneagent.features'),
		('Problem Alerting Profiles', '/ui/settings/builtin:alerting.profile'),
		('Problem Notifications', '/ui/settings/builtin:problem.notifications'),
		('Request Attributes', '#settings/requestattributes'),
	]

	drilldown_title = '## {{.title}}  \\n'

	dashboard_template = '''{
  "metadata": {
    "configurationVersions": [
      6
    ],
    "clusterVersion": "1.240.132.20220503-084001"
  },
  "id": "00000000-dddd-bbbb-ffff-000000000800",
  "dashboardMetadata": {
    "name": "TEMPLATE: Administration",
    "shared": true,
    "preset": true,
    "owner": "nobody@example.com"
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
        "height": 304
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
        "top": 304,
        "left": 0,
        "width": 494,
        "height": 304
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
        "left": 494,
        "width": 494,
        "height": 608
      },
      "tileFilter": {},
      "isAutoRefreshDisabled": false,
	  "markdown": "{{.setting_markdown}}"
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

	setting_markdown_title = drilldown_title.replace('{{.title}}', 'Settings')
	setting_markdown = setting_markdown_title
	for setting_link in setting_links:
		setting_key, setting_link = setting_link
		setting_markdown += f'  \\n[{setting_key}]({setting_link})'

	dashboard_template = dashboard_template.replace('{{.dashboard_markdown}}', dashboard_markdown)
	dashboard_template = dashboard_template.replace('{{.view_markdown}}', view_markdown)
	dashboard_template = dashboard_template.replace('{{.setting_markdown}}', setting_markdown)

	print(dashboard_template)

	write_json(directory_path, dashboard_name, json.loads(dashboard_template))

def write_json(directory_path, filename, json_dict):
	# print('write_json(' + directory_path + ',' + filename + ',' + str(json_dict) + ')')
	file_path = f'{directory_path}/{filename}'
	with open(file_path, 'w', encoding='utf-8') as file:
		file.write(json.dumps(json_dict, indent=4, sort_keys=False))


if __name__ == '__main__':
	main()
