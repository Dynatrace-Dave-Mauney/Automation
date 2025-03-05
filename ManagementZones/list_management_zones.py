"""
List Management Zones from a tenant.
"""

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
	endpoint = '/api/config/v1/managementZones'
	lines = []
	r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
	res = r.json()
	for entry in res['values']:
		management_zone_name = entry.get('name')
		lines.append(f'{management_zone_name}')

	print('Management Zones')
	if lines:
		print('name')
		for line in sorted(lines):
			print(line)


def run():
	friendly_function_name = 'Dynatrace Automation Reporting'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'PreProd'
	# env_name_supplied = 'Sandbox'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
	process(env, token)


if __name__ == '__main__':
	run()
