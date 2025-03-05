"""
Save management zones from the tenant to the path indicated below.
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


def save_management_zones(env, token, path):
	endpoint = '/api/config/v1/managementZones'
	download_count = 0
	management_zone_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
	for management_zone_json in management_zone_json_list:
		for entry in management_zone_json.get('values'):
			management_zone_name = entry.get('name')
			management_zone_id = entry.get('id')
			print(management_zone_id, management_zone_name)
			r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{management_zone_id}', token)
			management_zone = r.json()
			clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{management_zone_id}.json')
			print(f'Saving {management_zone_name} ({management_zone_id}) to {clean_filename}')
			save(path, clean_filename, management_zone)
			download_count += 1

	print(f'Downloaded {download_count} management_zones to {path}')


def main(arguments):
	usage = '''
	download_management_zones.py: Save selected or all management_zones from the tenant/environment 
	specified via command line argument.

	Usage:    
	
	download_management_zones.py <tenant/environment URL> <token>
	
	Examples: 
	
	download_management_zones.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123
	download_management_zones.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123
	'''

	print('args' + str(arguments))
	print(os.getcwd())

	friendly_function_name = 'Dynatrace Automation'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Upper'
	# env_name_supplied = 'Lower'
	# env_name_supplied = 'Sandbox'
	#
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'PreProd'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

	path = f'../$Output/ManagementZones/Downloads/{env_name}_BACKUP'

	print(f'Downloading management_zones for {env_name} to {path}')

	if len(arguments) == 1:
		save_management_zones(env, token, path)
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
			save_management_zones(arguments[1], arguments[2], arguments[3])
		else:
			print(usage)
			raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
	main(sys.argv)
