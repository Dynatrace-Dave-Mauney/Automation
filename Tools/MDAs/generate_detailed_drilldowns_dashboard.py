"""
Generate "Detailed Drilldowns Menu" Dashboard JSON.
"""

import json

# directory_path = '../../Dashboards/Curated/Details'
# dashboard_name = 'Detailed_Drilldowns_Menu.json'

directory_path = '../../Dashboards/Templates/Overview'
dashboard_name = '00000000-dddd-bbbb-ffff-000000000900.json'

def main():
	# Application out of the box links
	application_links = [
		('Frontend/Applications', '#uemapplications'),
		('Web Applications', '#uemapplications;appsshown=webapps'),
		('Mobile Applications', '#uemapplications;appsshown=mobileapps'),
		('Custom Applications', '#uemapplications;appsshown=customapps'),
		('Session Segmentation', '/ui/user-sessions'),
		('Query User Sessions', '/ui/user-sessions/query'),
		('Session Replay', '/ui/user-sessions/replay-landing'),
	]

	# Synthetic out-of-the-box links
	synthetic_links = [
		('Synthetic', '#monitors'),
	]

	# Service out-of-the-box links
	service_links = [
		('Services', '/ui/services'),
		('Distributed Traces/PurePaths', '/ui/diagnostictools/purepaths'),
		('Multidimensional Analysis', '/ui/diagnostictools'),
		('Top Web Requests', '/ui/diagnostictools/mda?mdaId=topweb'),
		('Top Database Statements', '/ui/diagnostictools/mda?mdaId=topdb'),
		('Exception Analysis', '/ui/diagnostictools/mda?mdaId=exceptions'),
	]

	# Require no request attributes or other dependencies
	service_generic_mda_names_and_params = [
		('HTTP 4xx Details',
		 'metric=REQUEST_COUNT&dimension=%7BHTTP-Status%7D%20%7BHTTP-Method%7D%20%7BRequest:Name%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11400-499'),
		('HTTP 4xx Summary',
		 'metric=REQUEST_COUNT&dimension=%7BHTTP-Status%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11400-499'),
		('HTTP 5xx Details',
		 'metric=REQUEST_COUNT&dimension=%7BHTTP-Status%7D%20%7BHTTP-Method%7D%20%7BRequest:Name%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11500-599'),
		('HTTP 5xx Summary',
		 'metric=REQUEST_COUNT&dimension=%7BHTTP-Status%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11500-599'),
		('HTTP 5xx by Exception',
		 'metric=HTTP_5XX_ERROR_COUNT&dimension=%7BException:Class%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E29%110%140'),
		('HTTP No Response Details',
		 'metric=REQUEST_COUNT&dimension=%7BHTTP-Status%7D%20%7BHTTP-Method%7D%20%7BRequest:Name%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11-1'),
		('Long Lock Times',
		 'metric=LOCK_TIME&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=P90&percentile=80&chart=COLUMN&servicefilter=0%1E20%111%144611686018427387'),
		('Long Wait Times',
		 'metric=WAIT_TIME&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=P90&percentile=80&chart=LINE&servicefilter=0%1E26%112%1026%111%1019%111000%144611686018427387'),
		('Slow Web Requests',
		 'metric=RESPONSE_TIME&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=AVERAGE&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%100%116000000%144611686018427387'),
		('Slow Web Requests: Percentile',
		 'metric=RESPONSE_TIME&dimension=%7BRequest:Name%7D%20&mergeServices=false&aggregation=P90&percentile=80&chart=COLUMN&servicefilter=0%1E26%111%1026%112%100%116000000%144611686018427387'),
	]

	# Require key requests or request attributes
	service_custom_mda_names_and_params = [
		('Key Requests: Failures',
		 'metric=FAILED_REQUEST_COUNT&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E61%110'),
		('Key Requests: Slowness',
		 'metric=RESPONSE_TIME&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=P90&percentile=80&chart=COLUMN&servicefilter=0%1E61%110%100%116000000%144611686018427387'),
		('Synthetic 4xx and 5xx Requests',
		 'metric=REQUEST_COUNT&dimension=%7BHTTP-Method%7D%20%7BURL:Host%7D%7BRelative-URL%7D%20%7BHTTP-Status%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%102%11400-599%1015%11aaaaaaaa-bbbb-cccc-dddd-000000000013%14DynatraceSynthetic'),
		('User Agent Type Summary',
		 'metric=REQUEST_COUNT&dimension=%7BRequestAttribute:User%20Agent%20Type%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E15%11aaaaaaaa-bbbb-cccc-dddd-000000000013'),
		('Health Checks',
		 'metric=REQUEST_COUNT&dimension=%7BRelative-URL%7D%20from%20%7BRequestAttribute:User%20Agent%20Type%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%112%1026%111%109%11Health%20Check%20Request%14Health%20Check%20Request'),
		('Tenable Calls',
		 'metric=REQUEST_COUNT&dimension=%7BHTTP-Method%7D%20%7BRequest:Name%7D%20%7BURL:Host%7D%20%7BRelative-URL%7D%20%7BHTTP-Status%7D&mergeServices=true&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E15%11aaaaaaaa-bbbb-cccc-dddd-000000000102%14%140%14%14%14%14'),
	]

	# Database out of the box links
	database_links = [
		('Databases', '/ui/databases'),
	]

	# Require no request attributes or other dependencies
	database_generic_mda_names_and_params = [
		('Failed Queries',
		 'metric=FAILED_REQUEST_COUNT&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=COUNT&percentile=80&chart=COLUMN&servicefilter=0%1E26%110%103%110'),
		('Number of DB Calls',
		 'metric=DATABASE_CHILD_CALL_COUNT&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=AVERAGE&percentile=80&chart=COLUMN&servicefilter=0%1E37%111%144611686018427387'),
		('Slow Queries',
		 'metric=RESPONSE_TIME&dimension=%7BRequest:Name%7D&mergeServices=false&aggregation=AVERAGE&percentile=80&chart=COLUMN&servicefilter=0%1E26%110%100%111000000%144611686018427387'),
	]

	# Process out of the box links
	process_links = [
		('Processes', '#newprocessessummary'),
		('CPU Profiling', '/ui/diagnostictools/profiling'),
		('Process Crashes', '#processcrashesglobal'),
		('Memory Dumps', '/ui/diagnostictools/memorydumps'),
	]

	# Host out of the box links
	host_links = [
		('Hosts', '#newhosts'),
		('Network', '/ui/network'),
	]

	# Other out-of-the-box links
	other_links = [
		('Smartscape', '#smartscape'),
		('AWS', '#awses'),
		('VMware', '#vcenters'),
		('Kubernetes', '/ui/kubernetes'),
		('Kubernetes Workloads', '/ui/entity/list/CLOUD_APPLICATION'),
		('Containers', '/ui/entity/list/CONTAINER_GROUP'),
		('Docker', '#docker'),
		('Extensions/Hub', '/ui/hub?#extensions'),
		('Custom Devices', '#newcustomdevices'),
	]

	drilldown_title = '___\\n## 🔍  {{.title}}\\n___'

	dashboard_template = '''{
	  "metadata": {
		"configurationVersions": [
		  6
		],
		"clusterVersion": "1.261.134.20230302-084304"
	  },
	  "id": "aaaaaaaa-bbbb-cccc-aaaa-000000000001",
	  "dashboardMetadata": {
		"name": "Detailed Drilldowns Menu",
		"shared": false,
		"owner": "dave.mauney@dynatrace.com",
		"hasConsistentColors": false
	  },
	  "tiles": [
		{
		  "name": "Markdown",
		  "tileType": "MARKDOWN",
		  "configured": true,
		  "bounds": {
			"top": 0,
			"left": 608,
			"width": 608,
			"height": 532
		  },
		  "tileFilter": {},
		  "isAutoRefreshDisabled": false,
		  "markdown": "{{.services_markdown}}"
		},
		{
		  "name": "Markdown",
		  "tileType": "MARKDOWN",
		  "configured": true,
		  "bounds": {
			"top": 532,
			"left": 608,
			"width": 608,
			"height": 266
		  },
		  "tileFilter": {},
		  "isAutoRefreshDisabled": false,
		  "markdown": "{{.databases_markdown}}"
		},
		{
		  "name": "Markdown",
		  "tileType": "MARKDOWN",
		  "configured": true,
		  "bounds": {
			"top": 0,
			"left": 1216,
			"width": 608,
			"height": 266
		  },
		  "tileFilter": {},
		  "isAutoRefreshDisabled": false,
		  "markdown": "{{.processes_markdown}}"
		},
		{
		  "name": "Markdown",
		  "tileType": "MARKDOWN",
		  "configured": true,
		  "bounds": {
			"top": 266,
			"left": 1216,
			"width": 608,
			"height": 266
		  },
		  "tileFilter": {},
		  "isAutoRefreshDisabled": false,
		  "markdown": "{{.hosts_markdown}}"
		},
		{
		  "name": "Markdown",
		  "tileType": "MARKDOWN",
		  "configured": true,
		  "bounds": {
			"top": 0,
			"left": 0,
			"width": 608,
			"height": 532
		  },
		  "tileFilter": {},
		  "isAutoRefreshDisabled": false,
		  "markdown": "{{.applications_markdown}}"
		},
		{
		  "name": "Markdown",
		  "tileType": "MARKDOWN",
		  "configured": true,
		  "bounds": {
			"top": 532,
			"left": 0,
			"width": 608,
			"height": 266
		  },
		  "tileFilter": {},
		  "isAutoRefreshDisabled": false,
		  "markdown": "{{.synthetics_markdown}}"
		},
		{
		  "name": "Markdown",
		  "tileType": "MARKDOWN",
		  "configured": true,
		  "bounds": {
			"top": 532,
			"left": 1216,
			"width": 608,
			"height": 266
		  },
		  "tileFilter": {},
		  "isAutoRefreshDisabled": false,
		  "markdown": "{{.others_markdown}}"
		}
	  ]
	}
	'''

	applications_markdown_title = drilldown_title.replace('{{.title}}', 'Applications')
	applications_markdown = applications_markdown_title
	for application_link in application_links:
		application_key, application_link = application_link
		applications_markdown += f'  \\n[{application_key}]({application_link})'

	synthetics_markdown_title = drilldown_title.replace('{{.title}}', 'Synthetics')
	synthetics_markdown = synthetics_markdown_title
	for synthetic_link in synthetic_links:
		synthetic_key, synthetic_link = synthetic_link
		synthetics_markdown += f'  \\n[{synthetic_key}]({synthetic_link})'

	mda_url_path = '/ui/diagnostictools/mda'
	services_markdown_title = drilldown_title.replace('{{.title}}', 'Services')
	services_markdown = services_markdown_title
	for service_link in service_links:
		service_key, service_link = service_link
		services_markdown += f'  \\n[{service_key}]({service_link})'
	for service_generic_mda_name_and_param in service_generic_mda_names_and_params:
		service_key, service_link = service_generic_mda_name_and_param
		services_markdown += f'  \\n [{service_key}]({mda_url_path}?{service_link})'
	for service_custom_mda_name_and_param in service_custom_mda_names_and_params:
		service_key, service_link = service_custom_mda_name_and_param
		services_markdown += f'  \\n[{service_key}]({mda_url_path}?{service_link})'

	databases_markdown_title = drilldown_title.replace('{{.title}}', 'Databases')
	databases_markdown = databases_markdown_title
	for database_link in database_links:
		database_key, database_link = database_link
		databases_markdown += f'  \\n[{database_key}]({database_link})'
	for database_generic_mda_name_and_param in database_generic_mda_names_and_params:
		database_key, database_link = database_generic_mda_name_and_param
		databases_markdown += f'  \\n[{database_key}]({mda_url_path}?{database_link})'

	processes_markdown_title = drilldown_title.replace('{{.title}}', 'Processes')
	processes_markdown = processes_markdown_title
	for process_link in process_links:
		process_key, process_link = process_link
		processes_markdown += f'  \\n[{process_key}]({process_link})'

	hosts_markdown_title = drilldown_title.replace('{{.title}}', 'Hosts')
	hosts_markdown = hosts_markdown_title
	for host_link in host_links:
		host_key, host_link = host_link
		hosts_markdown += f'  \\n[{host_key}]({host_link})'

	others_markdown_title = drilldown_title.replace('{{.title}}', 'Others')
	others_markdown = others_markdown_title
	for other_link in other_links:
		other_key, other_link = other_link
		others_markdown += f'  \\n[{other_key}]({other_link})'

	dashboard_template = dashboard_template.replace('{{.applications_markdown}}', applications_markdown)
	dashboard_template = dashboard_template.replace('{{.synthetics_markdown}}', synthetics_markdown)
	dashboard_template = dashboard_template.replace('{{.services_markdown}}', services_markdown)
	dashboard_template = dashboard_template.replace('{{.databases_markdown}}', databases_markdown)
	dashboard_template = dashboard_template.replace('{{.processes_markdown}}', processes_markdown)
	dashboard_template = dashboard_template.replace('{{.hosts_markdown}}', hosts_markdown)
	dashboard_template = dashboard_template.replace('{{.others_markdown}}', others_markdown)

	print(dashboard_template)

	write_json(directory_path, dashboard_name, json.loads(dashboard_template))

def write_json(directory_path, filename, json_dict):
	# print('write_json(' + directory_path + ',' + filename + ',' + str(json_dict) + ')')
	file_path = f'{directory_path}/{filename}'
	with open(file_path, 'w') as file:
		file.write(json.dumps(json_dict, indent=4, sort_keys=False))


if __name__ == '__main__':
	main()
