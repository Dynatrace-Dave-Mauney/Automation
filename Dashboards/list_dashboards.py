"""
List dashboards from a tenant.
"""

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
	endpoint = '/api/config/v1/dashboards'
	lines = []
	r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
	res = r.json()
	for entry in res['dashboards']:
		dashboard_name = entry.get('name')
		dashboard_id = entry.get('id')
		dashboard_owner = entry.get('owner')
		# if dashboard_owner == 'Dynatrace':
		# if dashboard_owner == 'dave.mauney@dynatrace.com' and \
		# 		not dashboard_id.startswith('aaaaaaaa-bbbb-cccc-dddd-00000000'):
		# if dashboard_id.startswith('FF'):
		# if dashboard_id.startswith('00000001-0000-0000-000'):
		# if dashboard_id.startswith('00000000-dddd') and not dashboard_id.startswith('00000000-dddd-bbbb'):
		if True:
			lines.append(f'{dashboard_name}|{dashboard_id}|{dashboard_owner}')

	if lines:
		print('name|id|owner')
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
