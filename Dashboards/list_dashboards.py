"""
List dashboards from a tenant.
"""
import requests

from Reuse import dynatrace_api
from Reuse import environment


def list_dashboards(env, token):
	print('name|id|owner')
	lines = []
	headers = {'Authorization': 'Api-Token ' + token}
	r = dynatrace_api.get_object_list(env, token, endpoint='/api/config/v1/dashboards')
	res = r.json()
	for entry in res['dashboards']:
		dashboard_name = entry.get('name')
		dashboard_id = entry.get('id')
		dashboard_owner = entry.get('owner')
		# if dashboard_owner == 'Dynatrace':
		if dashboard_owner == 'dave.mauney@dynatrace.com' and \
				not dashboard_id.startswith('aaaaaaaa-bbbb-cccc-dddd-00000000'):
			lines.append(f'{dashboard_name}|{dashboard_id}|{dashboard_owner}')
	for line in sorted(lines):
		print(line)


def run():
	# env_name, env, token = environment.get_environment('Prod')
	# env_name, env, token = environment.get_environment('Prep')
	# env_name, env, token = environment.get_environment('Dev')
	env_name, env, token = environment.get_environment('Personal')
	# env_name, env, token = environment.get_environment('FreeTrial1')

	list_dashboards(env, token)


if __name__ == '__main__':
	run()
