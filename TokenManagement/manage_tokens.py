from inspect import currentframe
import json
import os
import requests
import ssl
# import time

endpoint = '/api/v2/apiTokens'

# env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'TOKEN_MANAGEMENT_PROD_TOKEN')
# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'TOKEN_MANAGEMENT_PREP_TOKEN')
# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'TOKEN_MANAGEMENT_DEV_TOKEN')
env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'TOKEN_MANAGEMENT_PERSONAL_TOKEN')

tenant = os.environ.get(tenant_key)
token = os.environ.get(token_key)
env = f'https://{tenant}.live.dynatrace.com'

def post(payload):
	json_dict = json.loads(payload)
	json_data = json.dumps(json_dict, indent=4, sort_keys=False)
	name = json_dict.get('name')
	scopes = json_dict.get('scopes')
	url = env + endpoint
	# print('POST: ' + url)
	# print('payload: ' + json_data)
	created_token = None
	try:
		r = requests.post(url, json_data.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
		if r.status_code == 201:
			created_token = json.loads(r.text).get('token')
			print('Created token ' + name + ' with scopes ' + str(scopes) + ': ' + created_token)
		else:
			print('Status Code: %d' % r.status_code)
			print('Reason: %s' % r.reason)
			if len(r.text) > 0:
				print(r.text)
			if r.status_code not in [200, 201, 204]:
				print(json_data)
				error_filename = '$post_error_payload.json'
				with open(error_filename, 'w') as file:
					file.write(json_data)
				print('Error in "post(payload)" method')
				print('Exit code shown below is the source code line number of the exit statement invoked')
				print('See ' + error_filename + ' for more details')
				exit(get_line_number())
	except ssl.SSLError:
		print('SSL Error')
		exit(get_line_number())

	return created_token


def put(token_id, payload):
	json_data = json.dumps(json.loads(payload), indent=4, sort_keys=False)
	url = env + endpoint + '/' + token_id
	# print('PUT: ' + url)
	# print('payload: ' + json_data)
	try:
		r = requests.put(url, json_data.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
		print('Status Code: %d' % r.status_code)
		print('Reason: %s' % r.reason)
		if len(r.text) > 0:
			print(r.text)
		if r.status_code not in [200, 201, 204]:
			print(json_data)
			with open('$post_error_payload.json', 'w') as file:
				file.write(json_data)
			exit(get_line_number())
		return r
	except ssl.SSLError:
		print('SSL Error')
		exit(get_line_number())


def get(token_id):
	token_split = token_id.split('.')
	token_key = token_split[0] + '.' + token_split[1]
	try:
		full_url = env + endpoint + '/' + token_key
		resp = requests.get(full_url, headers={'Authorization': 'Api-Token ' + token})
		if resp.status_code != 200:
			print('REST API Call Failed!')
			print(f'GET {full_url} {resp.status_code} - {resp.reason}')
			print(resp.text)
		else:
			return json.loads(resp.text)
	except ssl.SSLError:
		print('SSL Error')
		exit(get_line_number())


def get_for_update(token_id):
	full_token = json.loads(get(token_id).text)
	api_token_name = full_token.get('name')
	api_token_enabled = full_token.get('enabled')
	api_token_scopes = full_token.get('scopes')
	update_token = {"name": api_token_name, "enabled": api_token_enabled, "scopes": api_token_scopes}
	return update_token


def delete(token_id):
	try:
		full_url = env + endpoint + '/' + token_id
		resp = requests.delete(full_url, headers={'Authorization': 'Api-Token ' + token})
		if resp.status_code != 200 and resp.status_code != 204:
			print('REST API Call Failed!')
			print(f'GET {full_url} {resp.status_code} - {resp.reason}')
			print(resp.text)
		else:
			print('Deleted: ' + token_id)
	except ssl.SSLError:
		print('SSL Error')
		exit(get_line_number())


def post_robot_admin():
	token_name = 'Robot Admin'
	return post('{"name":"' + token_name + '","scopes":["activeGates.read","activeGateTokenManagement.read","apiTokens.read","auditLogs.read","credentialVault.read","entities.read","events.read","extensionConfigurations.read","extensionEnvironment.read","extensions.read","geographicRegions.read","hub.read","metrics.read","networkZones.read","problems.read","releases.read","settings.read","settings.write","slo.read","syntheticExecutions.read","syntheticLocations.read","CaptureRequestData","DataExport","DataImport","DssFileManagement","DTAQLAccess","ExternalSyntheticIntegration","ReadConfig","ReadSyntheticData","WriteConfig"]}')


def post_monaco():
	token_name = 'Monaco'
	return post('{"name":"' + token_name + '","scopes":["slo.read","credentialVault.read","DataExport","ReadConfig","ReadSyntheticData","WriteConfig", "CaptureRequestData"]}')


def post_reporting():
	token_name = 'Reporting'
	return post('{"name":"' + token_name + '","scopes":["activeGates.read","activeGateTokenManagement.read","apiTokens.read","auditLogs.read","entities.read","events.read","extensionConfigurations.read","extensionEnvironment.read","extensions.read","metrics.read","networkZones.read","problems.read","releases.read","settings.read","slo.read","syntheticLocations.read","credentialVault.read","DataExport","DssFileManagement","ReadConfig","ReadSyntheticData"]}')


def post_terraform_read():
	token_name = 'Terraform Read'
	return post('{"name":"' + token_name + '","scopes":["settings.read","slo.read","CaptureRequestData","ExternalSyntheticIntegration","ReadConfig"]}')


def post_super_reader():
	# Without Log Access since my user does not have that permission
	token_name = 'Super Reader'
	return post('{"name":"' + token_name + '","scopes":["activeGates.read","activeGateTokenManagement.read","apiTokens.read","entities.read","events.read","extensionConfigurations.read","extensionEnvironment.read","extensions.read","geographicRegions.read","hub.read","metrics.read","networkZones.read","problems.read","releases.read","settings.read","slo.read","syntheticExecutions.read","syntheticLocations.read","credentialVault.read","DataExport","DataImport","ExternalSyntheticIntegration","ReadConfig","ReadSyntheticData"], "expirationDate":"2023-04-01T00:00:00.000Z"}')


def post_api_token_read_write():
	token_name = 'API Tokens (Read/Write)'
	return post('{"name":"' + token_name + '","scopes":["apiTokens.read", "apiTokens.write"]}')


def post_test_token():
	token_name = 'Test'
	return post('{"name":"' + token_name + '","scopes":["ReadConfig"]}')


def post_esa():
	token_name = 'ESA'
	return post('{"name":"' + token_name + '","scopes":["activeGates.read","auditLogs.read","entities.read","events.read","extensionConfigurations.read","extensionEnvironment.read","extensions.read","geographicRegions.read","metrics.read","networkZones.read","problems.read","settings.read","slo.read","syntheticLocations.read","DataExport","DTAQLAccess","ReadConfig","ReadSyntheticData"]}')


def post_mute_tenable_token():
	token_name = 'Mute Tenable'
	return post('{"name":"' + token_name + '","scopes":["entities.read", "settings.read", "settings.write"]}')


def post_dashboard_generator():
	token_name = 'Dashboard Generator'
	return post('{"name":"' + token_name + '","scopes":["metrics.read","ReadConfig","WriteConfig"]}')


def post_logs_ingest():
	token_name = 'Logs Ingest'
	return post('{"name":"' + token_name + '","scopes":["logs.ingest"]}')


def post_read_metrics():
	token_name = 'Read Metrics'
	return post('{"name":"' + token_name + '","scopes":["metrics.read"]}')


def rotate_token(token_id):
	old_token = get(token_id)
	old_token.pop('id')
	old_token.pop('creationDate')
	new_token = post(json.dumps(old_token))
	delete(token_id)
	print('Rotatated tokens: ' + token_id + ' -> ' + new_token)
	return new_token


def list_tokens():
	try:
		full_url = env + endpoint
		resp = requests.get(full_url, headers={'Authorization': 'Api-Token ' + token})
		if resp.status_code != 200:
			print('REST API Call Failed!')
			print(f'GET {full_url} {resp.status_code} - {resp.reason}')
			print(resp.text)
		else:
			token_dict = json.loads(resp.text)
			total_count = token_dict.get('totalCount')
			page_size = token_dict.get('pageSize')
			print('Total Token Count: ' + str(total_count))
			print('Page Size: ' + str(page_size))
			print('Pagination not yet supported...')
			api_tokens = token_dict.get('apiTokens')
			formatted_api_tokens = []
			for api_token in api_tokens:
				api_token_id = api_token.get('id')
				api_token_name = api_token.get('name')
				api_token_enabled = api_token.get('enabled')
				api_token_owner = api_token.get('owner')
				api_token_creation_date = api_token.get('creationDate')
				formatted_api_token = api_token_name + '|' + api_token_owner + '|' + str(api_token_enabled) + '|' + api_token_creation_date + '|' + api_token_id
				formatted_api_tokens.append(formatted_api_token)
			for formatted_api_token in sorted(formatted_api_tokens):
				print(formatted_api_token)
	except ssl.SSLError:
		print('SSL Error')
		exit(get_line_number())


def lookup_by_secret(secret):
	payload = '{"token": "' + secret + '"}'
	json_data = json.dumps(json.loads(payload), indent=4, sort_keys=False)
	url = env + endpoint + '/lookup'
	try:
		r = requests.post(url, json_data.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
		# print('Status Code: %d' % r.status_code)
		# print('Reason: %s' % r.reason)
		# if len(r.text) > 0:
		# 	print(r.text)
		if r.status_code not in [200, 201, 204]:
			print(json_data)
			with open('$post_error_payload.json', 'w') as file:
				file.write(json_data)
			exit(get_line_number())
		return json.loads(r.text)
	except ssl.SSLError:
		print('SSL Error')
		exit(get_line_number())


def get_line_number():
	cf = currentframe()
	return cf.f_back.f_lineno


def process():
	# For when all is commented below...
	pass

	if not tenant or not token:
		print('Tenant or Token Environment Variable Not Set!')
		exit(1)

	print('Environment:     ' + env_name)
	print('Environment URL: ' + env)

	exit(1234)

	# Testing

	# # Test token creation
	test_token = post_test_token()
	# monaco_token = post_monaco()
	# reporting_token = post_reporting()
	# terraform_read_token = post_terraform_read()
	# super_reader_token = post_super_reader()
	# api_token_read_write_token = post_api_token_read_write()
	# esa_token = post_esa()
	# mute_tenable_token = post_mute_tenable_token()
	# dashboard_generator_token = post_dashboard_generator()
	# logs_ingest_token = post_logs_ingest()
	# robot_admin_token = post_robot_admin()
	# read_metrics_token = post_read_metrics()
	#
	# # Test getting a token
	# print('get:', get(test_token))
	#
	# # Test looking up a token by a secret
	# print('lookup_by_secret:', lookup_by_secret(test_token))
	#
	# # Test deleting tokens
	delete(test_token)
	# delete(monaco_token)
	# delete(reporting_token)
	# delete(terraform_read_token)
	# delete(super_reader_token)
	# delete(api_token_read_write_token)
	# delete(esa_token)
	# delete(mute_tenable_token)
	# delete(dashboard_generator_token)
	# delete(logs_ingest_token)
	# delete(robot_admin_token)
	# delete(read_metrics_token)
	#
	# # Test token rotation
	# test_token = post_test_token()
	# new_token = rotate_token(test_token)
	# delete(new_token)
	#
	# # Test listing tokens
	# list_tokens()

	# Safety Exit
	exit(1234)

	# Usage Examples

	# Simple delete example
	# delete('dt0c01.*')

	# for token_to_delete in ['dt0c01.*', 'dt0c01.**', 'dt0c01.***']:
	# 	delete(token_to_delete)

	# Simple update example
	# api_token = get_for_update('dt0c01.*')
	# api_token['enabled'] = True
	# put('dt0c01.*', json.dumps(api_token))

	# Simple lookup_by_secret example
	# print(lookup_by_secret('dt0c01.*.*').text)

	# In case ever needed:
	# print('Waiting for eventual consistency...')
	# time.sleep(10)


if __name__ == '__main__':
	process()
