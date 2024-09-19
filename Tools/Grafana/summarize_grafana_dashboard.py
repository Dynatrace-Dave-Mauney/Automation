import json
import os
import xlsxwriter

from Reuse import environment

# get from configurations.yaml
root_directory = 'GrafanaDashboards/customer_specific'
grafana_data = []


def save_grafana_dashboard_summary_data(filename, panel_title, panel_type, datasource_type, display_mode, target_measurement):
	data = [filename, panel_title, panel_type, datasource_type, display_mode, target_measurement]
	grafana_data.append(data)


def write_grafana_dashboard_summary_xlsx():
	workbook = xlsxwriter.Workbook('GrafanaDashboardSummary.xlsx')
	worksheet = workbook.add_worksheet('Summary')

	# Add a bold format to use to highlight cells.
	bold = workbook.add_format({'bold': True})

	# Write headers in bold
	worksheet.write('A1', 'File Name', bold)
	worksheet.write('B1', 'Panel Title', bold)
	worksheet.write('C1', 'Panel Type', bold)
	worksheet.write('D1', 'Datasource Type', bold)
	worksheet.write('E1', 'Target Measurement', bold)
	worksheet.write('F1', 'Display Mode', bold)
	# filename, panel_title, panel_type, datasource_type, display_mode, target_measurement
	row = 1

	for inner_list in grafana_data:
		for filename, panel_title, panel_type, datasource_type, display_mode, target_measurement in [inner_list]:
			worksheet.write(row, 0, filename)
			worksheet.write(row, 1, panel_title)
			worksheet.write(row, 2, panel_type)
			worksheet.write(row, 3, datasource_type)
			worksheet.write(row, 4, display_mode)
			worksheet.write(row, 5, target_measurement)
		row += 1

	workbook.close()


def process_grafana_dashboard(filename):
	dashboard = read_json(filename)
	panels = dashboard.get('panels')
	for panel in panels:
		panel_title = panel.get('title')
		panel_type = panel.get('type')

		display_mode = None
		options = panel.get('options')
		# print(f'options: {options}')
		if options:
			legend = options.get('legend')
			if legend:
				display_mode = legend.get('displayMode')
				# print(f'display_mode: {display_mode}')

		datasource_type = None
		datasource = panel.get('datasource')
		if datasource:
			datasource_type = datasource.get('type')

		target_measurement = None
		targets = panel.get('targets')
		if targets:
			print(f'targets: {targets}')
			for target in targets:
				target_measurement = target.get('measurement')
				if not target_measurement:
					target_measurement = target.get('expr')
				print(f'target_measurement: {target_measurement}')
				target_datasource_type = target.get('dsType')
				if not target_datasource_type:
					target_datasource_type = target.get('datasource')
				print(f'target_datasource_type: {target_datasource_type}')
				print(panel_title, panel_type, datasource_type, display_mode, target_measurement)
				save_grafana_dashboard_summary_data(filename, panel_title, panel_type, datasource_type, display_mode, target_measurement)


def read_json(filename):
	with open(filename, 'r', encoding='utf-8') as file:
		json_data = json.loads(file.read())
		return json_data


def process_grafana_dashboards():
	configuration_file = 'configurations.yaml'
	global root_directory
	root_directory = environment.get_configuration('root_directory', configuration_file=configuration_file)

	print(root_directory)

	filenames = [os.path.join(path, name) for path, subdirs, files in os.walk(root_directory) for name in files]
	for filename in filenames:
		if filename.endswith('.json'):
			process_grafana_dashboard(filename)

	write_grafana_dashboard_summary_xlsx()


def main():
	process_grafana_dashboards()


if __name__ == '__main__':
	main()
