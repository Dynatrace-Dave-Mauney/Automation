"""
Save dashboards from the tenant to the path indicated below.
"""
import json
import os
import re
import requests
import ssl
import sys


def save(path, file, content):
	if not os.path.isdir(path):
		os.makedirs(path)
	with open(path + "/" + file, "w", encoding='utf8') as text_file:
		text_file.write("%s" % json.dumps(content, indent=4))


def save_dashboards(env, token, path):
	try:
		headers = {'Authorization': 'Api-Token ' + token}
		r = requests.get(env + '/api/config/v1/dashboards', headers=headers)
		# print("%s save list: %d" % ('dashboards', r.status_code))
		# print(r.content)
		res = r.json()
		# print(res)
		# print('Saving to directory path: ' + path)
		for entry in res['dashboards']:
			dashboard_name = entry.get('name')
			dashboard_id = entry.get('id')
			dashboard_owner = entry.get('owner')
			# if dashboard_id.startswith('00000000-dddd-bbbb-ffff-0000000000'):
			# if ((dashboard_name.startswith('Prod:') or dashboard_name.startswith('Prep:')) and dashboard_id.startswith('00000000-dddd-bbbb-ffff-0000000000')):
			# if dashboard_owner == 'Dynatrace' and dashboard_name.startswith('A'):
			# if dashboard_owner == 'nobody@example.com':
			# if dashboard_owner == 'Dynatrace':
			if True:
				response = requests.get(env + '/api/config/v1/dashboards/' + dashboard_id, headers=headers)
				dashboard = response.json()
				if 'ism74021' in str(dashboard):
					clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{dashboard_name}.json')
					print(f'Saving {dashboard_name} ({dashboard_id}) owned by {dashboard_owner} to {clean_filename}')
					save(path, clean_filename, dashboard)
	except ssl.SSLError:
		print("SSL Error")

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

	env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
	# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
	# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
	# env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

	tenant = os.environ.get(tenant_key)
	token = os.environ.get(token_key)
	env = f'https://{tenant}.live.dynatrace.com'

	path = f'../$Output/Dashboards/Downloads/{env_name}'

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
