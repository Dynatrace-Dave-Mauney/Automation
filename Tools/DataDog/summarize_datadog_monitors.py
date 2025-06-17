import json
import os
import xlsxwriter

from Reuse import environment

# get from configurations.yaml
root_directory = 'customer_specific/monitors'
datadog_data = []


def save_datadog_monitor_summary_data(filename, monitor_name, monitor_id, monitor_type, monitor_query, monitor_tags):
	data = [filename, monitor_name, monitor_id, monitor_type, monitor_query, monitor_tags]
	datadog_data.append(data)


def write_datadog_monitor_summary_xlsx():
	workbook = xlsxwriter.Workbook('DataDogMonitorSummary.xlsx')
	worksheet = workbook.add_worksheet('Summary')

	# Add a bold format to use to highlight cells.
	bold = workbook.add_format({'bold': True})

	# Write headers in bold
	worksheet.write('A1', 'File Name', bold)
	worksheet.write('B1', 'Monitor Name', bold)
	worksheet.write('C1', 'Type', bold)
	worksheet.write('D1', 'Query', bold)
	worksheet.write('E1', 'Tags', bold)
	row = 1

	for inner_list in datadog_data:
		for filename, monitor_name, monitor_id, monitor_type, monitor_query, monitor_tags in [inner_list]:
			worksheet.write(row, 0, filename)
			worksheet.write(row, 1, monitor_name)
			worksheet.write(row, 2, monitor_id)
			worksheet.write(row, 3, monitor_type)
			worksheet.write(row, 4, monitor_query)
			worksheet.write(row, 5, str(monitor_tags))
		row += 1

	workbook.close()


def process_datadog_monitor(filename):
	monitors = read_json(filename)
	print(monitors)
	
	for monitor in monitors:
		monitor_name = monitor.get('name')
		monitor_id = monitor.get('id')
		monitor_type = monitor.get('type')
		monitor_query = monitor.get('query')
		monitor_tags = monitor.get('tags')
		print(monitor_name, monitor_id, monitor_type, monitor_query, monitor_tags)

		save_datadog_monitor_summary_data(filename, monitor_name, monitor_id, monitor_type, monitor_query, monitor_tags)


def read_json(filename):
	with open(filename, 'r', encoding='utf-8') as file:
		json_data = json.loads(file.read())
		return json_data


def process_datadog_monitors():
	configuration_file = 'configurations.yaml'
	global root_directory
	root_directory = environment.get_configuration('monitors_root_directory', configuration_file=configuration_file)

	print(root_directory)

	filenames = [os.path.join(path, name) for path, subdirs, files in os.walk(root_directory) for name in files]
	for filename in filenames:
		if filename.endswith('.json'):
			process_datadog_monitor(filename)

	write_datadog_monitor_summary_xlsx()


def main():
	process_datadog_monitors()


if __name__ == '__main__':
	main()
