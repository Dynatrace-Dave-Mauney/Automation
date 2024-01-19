"""
List dashboards from a tenant that have 'Browser' in the dashboard name, but reference 'HTTP' metrics and vice versa.
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
		if 'Browser SLO' in dashboard_name:
			r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{dashboard_id}', token)
			dashboard_json = r.json()
			tiles = dashboard_json.get('tiles')
			if 'builtin:synthetic.http.' in str(tiles).lower():
				lines.append(f'{dashboard_name}|{dashboard_id}|{dashboard_owner}')
		if 'HTTP SLO' in dashboard_name:
			r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{dashboard_id}', token)
			dashboard_json = r.json()
			tiles = dashboard_json.get('tiles')
			if 'builtin:synthetic.browser.' in str(tiles).lower():
				print(dashboard_name, tiles)
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
	# env_name_supplied = 'PreProd'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
	process(env, token)


if __name__ == '__main__':
	run()
