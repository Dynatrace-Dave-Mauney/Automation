"""
List dashboards from a tenant.
"""
import os
import requests
import ssl


def list_dashboards(env, token):
	try:
		print('name|id|owner')
		lines = []
		headers = {'Authorization': 'Api-Token ' + token}
		r = requests.get(env + '/api/config/v1/dashboards', headers=headers)
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
	except ssl.SSLError:
		print("SSL Error")


def run():
	env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
	# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
	# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
	# env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

	tenant = os.environ.get(tenant_key)
	token = os.environ.get(token_key)
	env = f'https://{tenant}.live.dynatrace.com'

	list_dashboards(env, token)


if __name__ == '__main__':
	run()
