from inspect import currentframe
import json
import os
import requests
import ssl

env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
# env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

tenant = os.environ.get(tenant_key)
token = os.environ.get(token_key)
env = f'https://{tenant}.live.dynatrace.com'


def dump_json(endpoint, object_id):
	r = get_by_object_id(endpoint, object_id)
	json_data = json.dumps(json.loads(r.text), indent=4, sort_keys=False)
	print(json_data)
	with open('$DUMP-' + object_id, 'w') as file:
		file.write(json_data)


def get_by_object_id(endpoint, object_id):
	url = env + endpoint + '/' + object_id
	# print('GET: ' + url)
	try:
		r = requests.get(url, params='', headers={'Authorization': 'Api-Token ' + token})
		if r.status_code not in [200]:
			exit(get_linenumber())
		return r
	except ssl.SSLError:
		print('SSL Error')
		exit(get_linenumber())


def get_object_list(endpoint):
	url = env + endpoint
	# print('GET: ' + url)
	try:
		r = requests.get(url, params='', headers={'Authorization': 'Api-Token ' + token})
		if r.status_code not in [200]:
			print(r.status_code)
			print(r.reason)
			exit(get_linenumber())
		return r
	except ssl.SSLError:
		print('SSL Error')
		exit(get_linenumber())


def get_linenumber():
	cf = currentframe()
	return cf.f_back.f_lineno


def process():
	# For when everything is commented out below...
	pass

	formatted_line_list = []
	endpoint = '/api/v2/entities?pageSize=4000&entitySelector=type%28EC2_INSTANCE%29&fields=fromRelationships.isAccessibleBy'
	r = get_object_list(endpoint)
	ec2_instance_json = json.loads(r.text)
	ec2_instance_list = ec2_instance_json.get('entities')
	for ec2_instance in ec2_instance_list:
		# print(ec2_instance)
		display_name = ec2_instance.get('displayName')
		if not display_name.startswith('UNKNOWN'):
			formatted_line_list.append(display_name)

	for display_name in sorted(formatted_line_list):
		print(display_name)


if __name__ == '__main__':
	process()
