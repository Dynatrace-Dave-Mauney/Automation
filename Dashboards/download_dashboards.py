"""
Save dashboards from the tenant to the path indicated below.
"""
import json
import os
import re
import sys

from Reuse import dynatrace_api
from Reuse import environment

known_collisions = [
	'22471a3e-4bb3-11ed-bdc3-0242ac120002',
	'3b9c20e2-dc58-4a91-8dcb-f6217dc869ac',
	'6b38732e-609c-44e2-b34d-0286717ecdab',
	'6b38732e-8c5c-4b32-80a1-7053ec8f37e1',
	'6b38732e-d26b-45c7-b107-ed85e87ff288',
	'b6fc0160-9332-454f-a7bc-7217b2ae540c',
	'c15f39a8-7d74-4b97-af28-0b17a20dc711',
	'c704bd72-92e9-452a-b40e-73e6f4df9f08',
	'22471a3e-4bb3-11ed-bdc3-0242ac120002',
	'3b9c20e2-dc58-4a91-8dcb-f6217dc869ac',
	'6b38732e-609c-44e2-b34d-0286717ecdab',
	'6b38732e-8c5c-4b32-80a1-7053ec8f37e1',
	'6b38732e-d26b-45c7-b107-ed85e87ff288',
	'b6fc0160-9332-454f-a7bc-7217b2ae540c',
	'c15f39a8-7d74-4b97-af28-0b17a20dc711',
	'c704bd72-92e9-452a-b40e-73e6f4df9f08',
]


def save(path, file, content):
	if not os.path.isdir(path):
		os.makedirs(path)
	with open(path + "/" + file, "w", encoding='utf8') as text_file:
		text_file.write("%s" % json.dumps(content, indent=4))


def save_dashboards(env, token, path):
	endpoint = '/api/config/v1/dashboards'
	download_count = 0
	r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
	dashboard_json = r.json()
	for entry in dashboard_json.get('dashboards'):
		dashboard_name = entry.get('name')
		dashboard_id = entry.get('id')
		dashboard_owner = entry.get('owner')
		print(dashboard_id, dashboard_name, dashboard_owner)
		# if dashboard_id.startswith('00000000-dddd-bbbb-ffff-0000000000'):
		# if ((dashboard_name.startswith('Prod:') or dashboard_name.startswith('Prep:')) and dashboard_id.startswith('00000000-dddd-bbbb-ffff-0000000000')):
		# if dashboard_owner == 'Dynatrace' and dashboard_name.startswith('A'):
		# if dashboard_owner == 'nobody@example.com':
		# if dashboard_owner == 'Dynatrace':
		# if dashboard_owner == 'dave.mauney@dynatrace.com' and 'SLO' in dashboard_name:
		# if 'TEMPLATE: Oracle' in dashboard_name:
		endpoint = '/api/config/v1/dashboards'
		if dashboard_id not in known_collisions and dashboard_name != 'Home':
			r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{dashboard_id}', token)
			dashboard = r.json()
			# dashboard_metadata = dashboard.get('dashboardMetadata')
			# dashboard_preset = dashboard_metadata.get('preset')
			# if 'ism74021' in str(dashboard):
			# aaaaaaaa-bbbb-cccc-dddd-1
			# aaaaaaaa-bbbb-cccc-eeee-f
			# if dashboard_preset:
			# if dashboard_preset and (dashboard_id.startswith('aaaaaaaa-bbbb-cccc-abcd-0000000000') or dashboard_id.startswith('aaaaaaaa-bbbb-cccc-eeee-f')):
			if True:
				clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{dashboard_id}.json')
				print(f'Saving {dashboard_name} ({dashboard_id}) owned by {dashboard_owner} to {clean_filename}')
				save(path, clean_filename, dashboard)
				download_count += 1

	print(f'Downloaded {download_count} dashboards to {path}')


def main(arguments):
	usage = '''
	download_dashboards.py: Save selected or all dashboards from the tenant/environment 
	specified via command line argument.

	Usage:    
	
	download_dashboards.py <tenant/environment URL> <token>
	
	Examples: 
	
	download_dashboards.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123
	download_dashboards.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123
	'''

	print('args' + str(arguments))
	print(os.getcwd())

	friendly_function_name = 'Dynatrace Automation'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'NonProd'
	# env_name_supplied = 'Prep'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

	path = f'../$Output/Dashboards/Downloads/{env_name}'

	print(f'Downloading dashboards for {env_name} to {path}')

	if len(arguments) == 1:
		save_dashboards(env, token, path)
		exit()

	if len(arguments) < 3:
		print(usage)
		raise ValueError('Too few arguments!')
	if len(arguments) > 4:
		print(help)
		raise ValueError('Too many arguments!')
	if arguments[1] in ['-h', '--help']:
		print(help)
	elif arguments[1] in ['-v', '--version']:
		print('1.0')
	else:
		if len(arguments) == 4:
			save_dashboards(arguments[1], arguments[2], arguments[3])
		else:
			print(usage)
			raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
	main(sys.argv)
