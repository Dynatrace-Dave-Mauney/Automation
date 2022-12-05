# Generate an ALLOW rule for every settings 2.0 schema id.
import os
import requests


def process(env, token):
	schemas = []

	allow1 = 'ALLOW settings:schemas:read, settings:objects:read settings:objects:write WHERE settings:schemaId = "'
	allow2 = '";'

	endpoint = '/api/v2/settings/schemas'
	params = ''
	settings_json_list = get_rest_api_json(env, token, endpoint, params)

	for settings_json in settings_json_list:
		inner_settings_json_list = settings_json.get('items')
		for inner_settings_json in inner_settings_json_list:
			schema_id = inner_settings_json.get('schemaId')
			schemas.append(schema_id)

	for schema in sorted(schemas):
		print(allow1 + schema + allow2)


def get_rest_api_json(url, token, endpoint, params):
	# print(f'get_rest_api_json({url}, {endpoint}, {params})')
	full_url = url + endpoint
	resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
	# print(f'GET {full_url} {resp.status_code} - {resp.reason}')
	if resp.status_code != 200 and resp.status_code != 404:
		print('REST API Call Failed!')
		print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
		exit(1)

	json_data = resp.json()

	# Some json is just a list of dictionaries.
	# Config V1 AWS Credentials is the only example I am aware of.
	# For these, I have never seen pagination.
	if type(json_data) is list:
		# DEBUG:
		# print(json_data)
		return json_data

	json_list = [json_data]
	next_page_key = json_data.get('nextPageKey')

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

		json_data = resp.json()
		# print(json_data)

		next_page_key = json_data.get('nextPageKey')
		json_list.append(json_data)

	return json_list


def main():
	# env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
	# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
	# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
	env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

	tenant = os.environ.get(tenant_key)
	token = os.environ.get(token_key)
	env = f'https://{tenant}.live.dynatrace.com'

	process(env, token)


if __name__ == '__main__':
	main()
