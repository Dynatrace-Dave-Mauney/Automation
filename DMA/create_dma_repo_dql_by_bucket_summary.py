import glob
import json
import os
import re

from collections import Counter
from json import JSONDecodeError
from pathlib import Path


DASHBOARD_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Dashboards'
NOTEBOOK_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Notebooks'

buckets_of_interest = [
	# Currently active in NonProd
	# fetch dt.system.buckets
	# | filter dt.system.table == "logs"
	# | filter records > 0
	'app_general',
	'ent_general',
	'ent_os',
	# From DMA Changes:
	# 'ent_aws',
	# 'app_ces',
	# 'app_ces',
	# 'app_ces',
	# 'ent_linux',
	# 'app_mobile',
	# 'ent_unix',
	# 'ent_windows',
	# 'ent_workstation',
	# 'is_proxy',
	# 'ent_zos',
	# 'ent_network',
]


def process():
	notebook_summary = load_notebook_summary()

	# print('Notebook Summary:')
	# for notebook in notebook_summary:
	# 	print(notebook)

	dashboard_summary = load_dashboard_summary()

	# print('Dashboard Summary:')
	# for dashboard in dashboard_summary:
	# 	print(dashboard)

	asset_summary = []
	asset_summary.extend(notebook_summary)
	asset_summary.extend(dashboard_summary)

	print('Asset Summary:')
	deduped_asset_summary = list(dict.fromkeys(sorted(asset_summary)))
	for asset in sorted(deduped_asset_summary):
		print(asset)

	print('Assets Referencing a Bucket of Interest:')
	deduped_asset_summary = list(dict.fromkeys(sorted(asset_summary)))
	for asset in sorted(deduped_asset_summary):
		bucket = re.sub('\|.*', '', asset)
		if bucket in buckets_of_interest:
			print(asset)

	bucket_list = []
	for asset in (asset_summary):
		bucket = re.sub('\|.*', '', asset)
		bucket_list.append(bucket)

	unique_bucket_count = len(set(bucket_list))
	print('Unique bucket count:', unique_bucket_count)

	bucket_reference_counts = Counter(bucket_list)
	print('Bucket references:', bucket_reference_counts)

	sorted_bucket_references_desc = dict(sorted(bucket_reference_counts.items(), key=lambda item: item[1], reverse=True))

	# for bucket_key in bucket_reference_counts.keys():
	for bucket_key in sorted_bucket_references_desc.keys():
		bucket_reference_count = bucket_reference_counts[bucket_key]
		print(f'{bucket_key}: {bucket_reference_count}')
	# print('Bucket references:', bucket_reference_counts)



def load_notebook_summary():
	results = []
	for filename in glob.glob(NOTEBOOK_REPO_PATH + '/*'):
		if os.path.isfile(filename):
			if 'metadata' not in filename and filename.endswith('.json'):
				file_stem = Path(filename).stem
				normalized_file_stem = file_stem.replace('[ALERT] - ', '')
				normalized_file_stem = normalized_file_stem.replace('[REPORT] - ', '')
				normalized_file_stem = normalized_file_stem.replace('[SEARCH] - ', '')

				with open(filename, 'r', encoding='utf-8') as f:
					infile_content = f.read()

				try:
					infile_content_json = json.loads(infile_content)
					# formatted_json = json.dumps(infile_content_json, indent=4, sort_keys=False)
					# print(formatted_json)
					notebook_sections = infile_content_json.get('sections')
					# print(notebook_sections)
					for notebook_section_value in notebook_sections:
						notebook_section_value_type = notebook_section_value.get('type')
						if notebook_section_value_type == 'dql':
							notebook_section_value_state = notebook_section_value.get('state')
							notebook_section_value_state_input_value = notebook_section_value_state.get('input', {}).get('value')
							# print(notebook_section_value_state_input_value)
							match = re.search(r'bucket:\s*\{"([^"]+)"\}', notebook_section_value_state_input_value)
							if match:
								bucket_name = match.group(1)
								# print('bucket:', bucket_name)
								# results.append(bucket_name)
								results.append(bucket_name + '|' + file_stem)
				except JSONDecodeError:
					print(f'Skipping due to non-JSON file content: {filename}')

	print('DEBUG: notebook repo results:')
	for result in sorted(results):
		print(result)

	return results


def load_dashboard_summary():
	results = []
	for filename in glob.glob(DASHBOARD_REPO_PATH + '/*'):
		if os.path.isfile(filename):
			if 'metadata' not in filename and filename.endswith('.json'):
				file_stem = Path(filename).stem
				normalized_file_stem = file_stem.replace('[Splunk] ', '')

				with open(filename, 'r', encoding='utf-8') as f:
					infile_content = f.read()

				try:
					infile_content_json = json.loads(infile_content)
					# formatted_json = json.dumps(infile_content_json, indent=4, sort_keys=False)
					# print(formatted_json)
					dashboard_tiles = infile_content_json.get('tiles')
					# print(dashboard_tiles)

					dashboard_tile_keys = dashboard_tiles.keys()
					# print(dashboard_tile_keys)
					for dashboard_tile_key in dashboard_tile_keys:
						dashboard_tile_dict = dashboard_tiles[dashboard_tile_key]
						# print(dashboard_tile_key)
						# print(dashboard_tile_dict)
						dashboard_tile_query = dashboard_tile_dict.get('query')
						if dashboard_tile_query:
							# print(dashboard_tile_query)

							match = re.search(r'bucket:\s*\{"([^"]+)"\}', dashboard_tile_query)
							if match:
								bucket_name = match.group(1)
								# print(bucket_name)
								results.append(bucket_name + '|' + file_stem)
				except JSONDecodeError:
					print(f'Skipping due to non-JSON file content: {filename}')


	print('DEBUG: dashboard repo results:')
	for result in sorted(results):
		print(result)

	return results


if __name__ == '__main__':
	process()
