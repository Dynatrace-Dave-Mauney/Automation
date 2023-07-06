"""
Save dashboards from the tenant to the path indicated below.
"""
import json
import os
import re
import sys

from Reuse import dynatrace_api
from Reuse import environment


def save(path, file, content):
	if not os.path.isdir(path):
		os.makedirs(path)
	with open(path + "/" + file, "w", encoding='utf8') as text_file:
		text_file.write("%s" % json.dumps(content, indent=4))


def save_dashboards(env, token, path):
	download_count = 0
	r = dynatrace_api.get_object_list(env, token, endpoint='/api/config/v1/dashboards')
	res = r.json()
	for entry in res['dashboards']:
		dashboard_name = entry.get('name')
		dashboard_id = entry.get('id')
		dashboard_owner = entry.get('owner')
		# if dashboard_id.startswith('00000000-dddd-bbbb-ffff-0000000000'):
		# if ((dashboard_name.startswith('Prod:') or dashboard_name.startswith('Prep:')) and dashboard_id.startswith('00000000-dddd-bbbb-ffff-0000000000')):
		# if dashboard_owner == 'Dynatrace' and dashboard_name.startswith('A'):
		# if dashboard_owner == 'nobody@example.com':
		# if dashboard_owner == 'Dynatrace':
		# if True:
		# if dashboard_owner == 'dave.mauney@dynatrace.com' and 'SLO' in dashboard_name:
		if 'TEMPLATE: Oracle' in dashboard_name:
			dashboard = dynatrace_api.get_by_object_id(env, token, endpoint='/api/config/v1/dashboards', object_id=dashboard_id)
			dashboard_metadata = dashboard.get('dashboardMetadata')
			dashboard_preset = dashboard_metadata.get('preset')
			# if 'ism74021' in str(dashboard):
			# aaaaaaaa-bbbb-cccc-dddd-1
			# aaaaaaaa-bbbb-cccc-eeee-f
			# if dashboard_preset:
			# if dashboard_preset and (dashboard_id.startswith('aaaaaaaa-bbbb-cccc-abcd-0000000000') or dashboard_id.startswith('aaaaaaaa-bbbb-cccc-eeee-f')):
			if True:
				clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{dashboard_name}.json')
				print(f'Saving {dashboard_name} ({dashboard_id}) owned by {dashboard_owner} to {clean_filename}')
				save(path, clean_filename, dashboard)
				download_count +=1

	print(f'Downloaded {download_count} dashboards to {path}')

def main(arguments):
	usage = '''
	download_dashboards.py: Save selected or all dashboards from the tenant/environment 
	specified via command line argument.

	Usage:    download_dashboards.py <tenant/environment URL> <token>
	Examples: download_dashboards.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123
			  download_dashboards.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123
	'''

	print('args' + str(arguments))
	print(os.getcwd())

	env_name, env, token = environment.get_environment('Prod')
	# env_name, env, token = environment.get_environment('Prep')
	# env_name, env, token = environment.get_environment('Dev')
	# env_name, env, token = environment.get_environment('Personal')
	# env_name, env, token = environment.get_environment('FreeTrial1')

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
