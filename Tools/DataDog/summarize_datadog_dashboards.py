import json
import os
import xlsxwriter

from Reuse import environment

# get from configurations.yaml
root_directory = 'customer_specific/dashboards'
datadog_data = []


def save_datadog_dashboard_summary_data(filename, dashboard_title, dashboard_description, widget_definition_title, widget_definition_type, query_name, query_data_source, query):
	data = [filename, dashboard_title, dashboard_description, widget_definition_title, widget_definition_type, query_name, query_data_source, query]
	datadog_data.append(data)


def write_datadog_dashboard_summary_xlsx():
	workbook = xlsxwriter.Workbook('DataDogDashboardSummary.xlsx')
	worksheet = workbook.add_worksheet('Summary')

	# Add a bold format to use to highlight cells.
	bold = workbook.add_format({'bold': True})

	# Write headers in bold
	worksheet.write('A1', 'File Name', bold)
	worksheet.write('B1', 'Dashboard Title', bold)
	worksheet.write('C1', 'Dashboard Description', bold)
	worksheet.write('D1', 'Widget Title', bold)
	worksheet.write('E1', 'Widget Type', bold)
	worksheet.write('F1', 'Query Name', bold)
	worksheet.write('G1', 'Query Data Source', bold)
	worksheet.write('H1', 'Query', bold)
	row = 1

	for inner_list in datadog_data:
		for filename, dashboard_title, dashboard_description, widget_definition_title, widget_definition_type, query_name, query_data_source, query in [inner_list]:
			worksheet.write(row, 0, filename)
			worksheet.write(row, 1, dashboard_title)
			worksheet.write(row, 2, dashboard_description)
			worksheet.write(row, 3, widget_definition_title)
			worksheet.write(row, 4, widget_definition_type)
			worksheet.write(row, 5, query_name)
			worksheet.write(row, 6, query_data_source)
			worksheet.write(row, 7, query)
		row += 1

	workbook.close()


def process_datadog_dashboard(filename):
	dashboard = read_json(filename)
	dashboard_title = dashboard.get('title')
	dashboard_description = dashboard.get('description')
	print(dashboard_title, dashboard_description)

	widgets = dashboard.get('widgets')
	for widget in widgets:
		widget_definition = widget.get('definition')
		widget_definition_title = widget_definition.get('title')
		widget_definition_type = widget_definition.get('type')
		if widget_definition_type not in ('query_value', 'timeseries'):
			print(f'Got unexpected type value of {widget_definition_type} for {widget_definition_title}')
			# exit(1)
		widget_definition_requests = widget_definition.get('requests')
		if len(widget_definition_requests) > 1:
			print(f'Got more requests than expected for {widget_definition_title}')
			# exit(1)

		if widget_definition_type in ('query_value', 'timeseries'):
			widget_definition_requests_queries = widget_definition_requests[0].get('queries')
			query_name = widget_definition_requests_queries[0].get('name')
			query_data_source = widget_definition_requests_queries[0].get('data_source')
			query = widget_definition_requests_queries[0].get('search').get('query')

			# print(widget_definition_title, widget_definition_type)
			# print(query_name, query_data_source, query)
			# print(widget_definition, widget_definition_requests, widget_definition_requests_queries)

			save_datadog_dashboard_summary_data(filename, dashboard_title, dashboard_description, widget_definition_title, widget_definition_type, query_name, query_data_source, query)


def read_json(filename):
	with open(filename, 'r', encoding='utf-8') as file:
		json_data = json.loads(file.read())
		return json_data


def process_datadog_dashboards():
	configuration_file = 'configurations.yaml'
	global root_directory
	root_directory = environment.get_configuration('dashboards_root_directory', configuration_file=configuration_file)

	print(root_directory)

	filenames = [os.path.join(path, name) for path, subdirs, files in os.walk(root_directory) for name in files]
	for filename in filenames:
		if filename.endswith('.json'):
			process_datadog_dashboard(filename)

	write_datadog_dashboard_summary_xlsx()


def main():
	process_datadog_dashboards()


if __name__ == '__main__':
	main()
