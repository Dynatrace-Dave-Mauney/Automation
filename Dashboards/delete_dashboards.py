# import requests, ssl, os, sys, json, glob
import os
import requests


def delete(url, token, endpoint, params):
	# print(f'get_rest_api_json({url}, {endpoint}, {params})')
	full_url = url + endpoint
	resp = requests.delete(full_url, params=params, headers={'Authorization': "Api-Token " + token})
	# print(f'DELTE {full_url} {resp.status_code} - {resp.reason}')
	if resp.status_code != 204:
		print('REST API Call Failed!')
		print(f'DELETE {full_url} {params} {resp.status_code} - {resp.reason}')
		exit(1)


def process(env_name, env, token):
	print('Environment Name:' + env_name)
	print('Environment URL: ' + env)

	endpoint = '/api/config/v1/dashboards'
	params = ''
	dashboards_json_list = get_rest_api_json(env, token, endpoint, params)

	count = 0
	delete_list = ['00000000-dddd-bbbb-ffff-000000000003']

	for dashboards_json in dashboards_json_list:
		inner_dashboards_json_list = dashboards_json.get('dashboards')
		for inner_dashboards_json in inner_dashboards_json_list:
			dashboard_id = inner_dashboards_json.get('id')
			name = inner_dashboards_json.get('name')
			owner = inner_dashboards_json.get('owner')
			print(dashboard_id, name, owner)

			# # # CAUTION HERE!!!! # # #
			# # # More flexible delete option is more dangerous! # # #
			# if owner.startswith('Dynatrace') and id.startswith('aaaaaaaa-bbbb-cccc-eeee-0000000000'):
			# 	delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

	delete_list = sorted(delete_list)

	if len(delete_list) > 0:
		print('DASHBOARDS TO BE DELETED: ')
		for line in delete_list:
			print(line)

		msg = 'PROCEED WITH DELETE OF LISTED DASHBOARDS?'
		proceed = input("%s (Y/n) " % msg).upper() == 'Y'

		if proceed:
			for line in delete_list:
				dashboard_id = line.split(':', 1)[0]
				endpoint = '/api/config/v1/dashboards/' + dashboard_id
				params = ''
				delete(env, token, endpoint, params)
				print('DELETED: ' + line)
				count += 1

	print('Dashboards Deleted: ' + str(count))


def get_rest_api_json(url, token, endpoint, params):
	# print(f'get_rest_api_json({url}, {endpoint}, {params})')
	full_url = url + endpoint
	resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
	# print(f'GET {full_url} {resp.status_code} - {resp.reason}')
	if resp.status_code != 200 and resp.status_code != 404:
		print('REST API Call Failed!')
		print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
		exit(1)

	json = resp.json()

	# Some json is just a list of dictionaries.
	# Config V1 AWS Credentials is the only example I am aware of.
	# For these, I have never seen pagination.
	if type(json) is list:
		# DEBUG:
		# print(json)
		return json

	json_list = [json]
	next_page_key = json.get('nextPageKey')

	while next_page_key is not None:
		# next_page_key = next_page_key.replace('=', '%3D') # Ths does NOT help.  Also, equals are apparently fine in params.
		# print(f'next_page_key: {next_page_key}')
		params = {'nextPageKey': next_page_key}
		full_url = url + endpoint
		resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
		# print(resp.url)

		if resp.status_code != 200:
			print('Paginated REST API Call Failed!')
			print(f'GET {full_url} {resp.status_code} - {resp.reason}')
			exit(1)

		json = resp.json()
		# print(json)

		next_page_key = json.get('nextPageKey')
		json_list.append(json)

	return json_list


def run():
	# env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
	# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
	# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
	env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

	tenant = os.environ.get(tenant_key)
	token = os.environ.get(token_key)
	env = f'https://{tenant}.live.dynatrace.com'

	process(env_name, env, token)


if __name__ == '__main__':
	run()
