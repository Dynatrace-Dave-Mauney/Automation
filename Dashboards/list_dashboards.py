"""
List dashboards from a tenant.
"""

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
	lines = []
	r = dynatrace_api.get_object_list(env, token, endpoint='/api/config/v1/dashboards')
	res = r.json()
	for entry in res['dashboards']:
		dashboard_name = entry.get('name')
		dashboard_id = entry.get('id')
		dashboard_owner = entry.get('owner')
		# if dashboard_owner == 'Dynatrace':
		# if dashboard_owner == 'dave.mauney@dynatrace.com' and \
		# 		not dashboard_id.startswith('aaaaaaaa-bbbb-cccc-dddd-00000000'):
		# if dashboard_id.startswith('FF'):
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
	# env_name_supplied = 'NonProd'
	# env_name_supplied = 'Prep'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
	process(env, token)


if __name__ == '__main__':
	run()
