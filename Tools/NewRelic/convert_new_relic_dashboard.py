import copy
import json
import os
import re
import xlsxwriter

from Reuse import environment

# get from configurations.yaml
keep_list = []
keep_page = ''
root_directory = 'NewRelicDashboards/customer_specific'

all_query_tokens = []

new_relic_data = []
dynatrace_dashboard_template = ''
id_prefix = 'faaaaaaa-faaa-faaa-fbbb-'


def save_new_relic_dashboard_summary_data(filename, new_relic_dashboard_name, page_name, widget_title, widget_visualization_id, widget_query, threshold_alert_severity, threshold_value):
	data = [filename, new_relic_dashboard_name, page_name, widget_title, widget_visualization_id, widget_query, threshold_alert_severity, threshold_value]
	# print('data:' + str(data))
	new_relic_data.append(data)


def write_new_relic_dashboard_summary_xlsx():
	workbook = xlsxwriter.Workbook('NewRelicDashboardSummary.xlsx')
	worksheet = workbook.add_worksheet('Summary')

	# Add a bold format to use to highlight cells.
	bold = workbook.add_format({'bold': True})

	# Write headers in bold
	worksheet.write('A1', 'File Name', bold)
	worksheet.write('B1', 'Name', bold)
	worksheet.write('C1', 'Page Name', bold)
	worksheet.write('D1', 'Widget Title', bold)
	worksheet.write('E1', 'Widget Visualization', bold)
	worksheet.write('F1', 'Widget Query', bold)
	worksheet.write('G1', 'Table', bold)
	worksheet.write('H1', 'Application', bold)

	row = 1

	for inner_list in new_relic_data:
		for filename, new_relic_dashboard_name, page_name, widget_title, widget_visualization_id, widget_query, threshold_alert_severity, threshold_value in [inner_list]:
			worksheet.write(row, 0, filename)
			worksheet.write(row, 1, new_relic_dashboard_name)
			worksheet.write(row, 2, page_name)
			worksheet.write(row, 3, widget_title)
			worksheet.write(row, 4, widget_visualization_id)
			worksheet.write(row, 5, widget_query)
			table = get_table_from_query(widget_query)
			application = get_application_from_query(widget_query)
			worksheet.write(row, 6, table)
			worksheet.write(row, 7, application)
		row += 1

	workbook.close()


"""
			table = get_table_from_query(widget_query)
			application = get_application_from_query(widget_query)

"""


def get_table_from_query(widget_query):
	table = re.sub('.* from ', '', widget_query.lower())
	table = re.sub('where .*', '', table)
	return table


def get_application_from_query(widget_query):
	widget_query = widget_query.lower()
	if 'appname' not in widget_query:
		return ''

	application = re.sub(".* where appname = '", '', widget_query.lower())
	application = re.sub(".* where appname='", '', application)
	print('1', application)
	application = re.sub("'.*", '', application)
	print('2', application)

	if application.startswith('select '):
		return ''

	return application


def process_new_relic_dashboard(filename):
	dashboard = read_json(filename)
	new_relic_dashboard_name = dashboard.get('name')
	# print(name)
	pages = dashboard.get('pages')
	# print(str(pages))
	for page in pages:
		# print(str(page))
		page_name = page.get('name')
		# print(page_name)
		widgets = page.get('widgets')
		# print(str(widgets))
		for widget in widgets:
			# print(str(widget))
			widget_title = widget.get('title')

			if keep_page and keep_list:
				if page_name == keep_page and widget_title in keep_list:
					pass
				else:
					continue

			# print(widget_title)
			widget_visualization = widget.get('visualization')
			widget_visualization_id = widget_visualization.get('id')
			# print(widget_visualization_id)
			widget_raw_configuration = widget.get('rawConfiguration')
			# print(widget_raw_configuration)
			widget_nrql_queries = widget_raw_configuration.get('nrqlQueries')
			# print(widget_nrql_queries)
			if widget_nrql_queries:
				for widget_nrql_query in widget_nrql_queries:
					# print(widget_nrql_query)
					widget_query = widget_nrql_query.get('query')
					# Workaround for carriage returns in string causing problems
					widget_query = widget_query.replace('\r ', '')
					analyze_query(widget_query)
					# widget_thresholds = widget_raw_configuration.get('thresholds')
					# print(widget_thresholds)
					# if widget_thresholds:
					# 	print(widget_thresholds)
					# 	for widget_threshold in widget_thresholds:
					# 		continue
					# 		print(widget_threshold)
					# 		threshold_alert_severity = widget_threshold.get('alertSeverity')
					# 		threshold_value = widget_threshold.get('value')
					# 		print(threshold_alert_severity + ':' + str(threshold_value))
					threshold_alert_severity = None
					threshold_value = None
					save_new_relic_dashboard_summary_data(filename, new_relic_dashboard_name, page_name, widget_title, widget_visualization_id, widget_query, threshold_alert_severity, threshold_value)


def read_json(filename):
	with open(filename, 'r', encoding='utf-8') as file:
		json_data = json.loads(file.read())
		return json_data


def process_new_relic_dashboards():
	configuration_file = 'configurations.yaml'
	global keep_list
	global keep_page
	global root_directory
	keep_list = environment.get_configuration('keep_list', configuration_file=configuration_file)
	keep_page = environment.get_configuration('keep_page', configuration_file=configuration_file)
	root_directory = environment.get_configuration('root_directory', configuration_file=configuration_file)

	print(root_directory, keep_page, keep_list)

	global dynatrace_dashboard_template
	dynatrace_dashboard_template = get_dashboard_template()
	# print(dynatrace_dashboard_template)
	filenames = [os.path.join(path, name) for path, subdirs, files in os.walk(root_directory) for name in files]
	for filename in filenames:
		if filename.endswith('.json'):
			process_new_relic_dashboard(filename)

	write_new_relic_dashboard_summary_xlsx()
	generate_dynatrace_dashboard()


def get_dashboard_template():
	# print('get_dashboard_template()')
	dashboard_template_file_name = 'dynatrace_dashboard_template.json'
	with open(dashboard_template_file_name, 'r', encoding='utf-8') as file:
		dashboard = json.loads(file.read())
		return dashboard


def generate_dynatrace_dashboard():
	# print('generate_dynatrace_dashboard()')
	dashboard = copy.deepcopy(dynatrace_dashboard_template)
	tiles = dashboard.get('tiles')
	# template_header = tiles[0]
	template_data_explorer = tiles[1]
	# print(template_header)
	# print(template_data_explorer)
	last_filename = None
	id_number = 1
	width = 304
	height = 304
	top = 0
	left = 0
	for inner_list in new_relic_data:
		for filename, new_relic_dashboard_name, page_name, widget_title, widget_visualization_id, widget_query, threshold_alert_severity, threshold_value in [inner_list]:
			if filename != last_filename:
				top = 0
				left = 0
				if last_filename is not None:
					write_dashboard(last_filename, dashboard)
					id_number += 1
				id = id_prefix + format_id_number(id_number)
				dashboard['id'] = id
				dashboard_metadata = dashboard.get('dashboardMetadata')
				dashboard_metadata['name'] = new_relic_dashboard_name
				dashboard['tiles'] = []
				last_filename = filename
			data_explorer_tile = copy.deepcopy(template_data_explorer)
			name = widget_title
			short_name = name
			name += ': ' + widget_query
			data_explorer_tile['name'] = name
			data_explorer_tile['customName'] = short_name
			# visualization_conversion = {'viz.pie': 'PIE_CHART', 'viz.bar': 'TOP_LIST', 'viz.table': 'TABLE', 'viz.billboard': 'SINGLE_VALUE', 'viz.line': 'GRAPH_CHART', 'viz.area': 'STACKED_AREA'}
			# dynatrace_vizualization = visualization_conversion[widget_visualization_id]
			# data_explorer_tile['visualConfig']['type'] = dynatrace_vizualization
			data_explorer_tile['bounds']['top'] = top
			data_explorer_tile['bounds']['left'] = left
			dashboard['tiles'].append(data_explorer_tile)
			if top >= 4712:
				print('Too many tiles...skipping this tile')
			else:
				if left >= (5 * width):  # Allow 6 Tiles per row
					top += height
					left = 0
				else:
					left += width

			write_dashboard(filename, dashboard)


def write_dashboard(filename, dashboard):
	# print('write_dashboard()')
	# print('filename: ' + filename)
	dashboard_file_name = filename.replace('NewRelic', 'Dynatrace')
	with open(dashboard_file_name, 'w') as file:
		file.write(json.dumps(dashboard, indent=4, sort_keys=False))
	print('wrote: ' + dashboard_file_name)


def format_id_number(id_number):
	len_zeros = 12 - len(str(id_number))
	zeros_string = '000000000000'[0:len_zeros]
	return zeros_string + str(id_number)


def analyze_query(query):
	# print('analyze_query(query)')
	print(query)
	query_tokens = query.split(' ')
	# print(query_tokens)
	for token in query_tokens:
		if token not in all_query_tokens:
			add_relevant_token(token)


def add_relevant_token(token):
	# print('add_relevant_token(token)')
	global all_query_tokens
	bad_first_chars = ["'", '"', "(", '=', '%', '-', '.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
	bad_last_chars = [')', "'", ',']
	if token == '' or token == '*' or token == 'Walgreens' or token == 'Metric' or token == 'Processed' or token in all_query_tokens:
		pass
	else:
		token_first_char = token[0]
		if token_first_char in bad_first_chars:
			pass
		else:
			token_last_char = token[-1]
			if token_last_char in bad_last_chars:
				pass
			else:
				if token.upper().startswith('IN'):
					pass
				else:
					if 'PERCENTAGE' in token.upper() or 'COUNT' in token.upper() or 'FROM' in token.upper() or '=' in token:
						pass
					else:
						if token.upper() not in ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'PLUS', 'UNTIL', 'AS', 'LIKE', 'LIMIT', 'FACET', 'TIMESERIES', 'AUTO', 'SINCE', 'MINUTE', 'MINUTES', 'AGO']:
							all_query_tokens.append(token)


def main():
	process_new_relic_dashboards()
	print('')
	print('Query Tokens:')
	for token in sorted(all_query_tokens):
		print(token)


if __name__ == '__main__':
	main()
