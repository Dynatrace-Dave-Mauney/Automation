"""
List dashboards from a path pattern.
"""

import glob
import json

# DASHBOARD_PATH = f'Templates/Overview/00000000-dddd-bbbb-ffff-0000000011??.json'
DASHBOARD_PATH = f'Custom/Overview-Prod/00000000-dddd-bbbb-ffff-00000000*.json'


def process():
	lines = []

	print('Only displaying dashboards with filters defined!')
	for filename in glob.glob(DASHBOARD_PATH):
		with open(filename, 'r', encoding='utf-8') as f:
			dashboard = f.read()
			dashboard_json = json.loads(dashboard)
			dashboard_id = dashboard_json.get('id')
			# print(dashboard_id)
			try:
				dashboard_filter = dashboard_json['dashboardMetadata']['dynamicFilters']['filters']
			except KeyError:
				dashboard_filter = []
			if dashboard_filter and len(dashboard_filter) > 0:
				dashboard_metadata = dashboard_json.get('dashboardMetadata')
				dashboard_name = dashboard_metadata.get('name').replace('TEMPLATE: ', '')
				lines.append(f"\t('{dashboard_name}', '#dashboard;id={dashboard_id}'),")

	if lines:
		for line in sorted(lines):
			print(line)


if __name__ == '__main__':
	process()
