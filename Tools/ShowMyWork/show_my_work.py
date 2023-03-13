# Report changes made via automation:
# RobotAdmin
# Dashboards/Templates
# Dashboards/Sandbox)

from inspect import currentframe
import json
import os
import requests
import ssl
from requests import Response

# env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

tenant = os.environ.get(tenant_key)
token = os.environ.get(token_key)
env = f'https://{tenant}.live.dynatrace.com'

fixed_id_startswith_list = {
	'aaaaaaaa-bbbb-cccc-dddd-000000000001',  # RobotAdmin Added Entities
	'00000000-dddd-bbbb-ffff-00000000',  # Dashboards/Templates/Overview
	'00000000-dddd-bbbb-aaaa-000000000',  # Dashboards/Sandbox
}


def process():
	print('Environment:     ' + env_name)
	print('Environment URL: ' + env)

	report_fixed_id_entities()


def report_fixed_id_entities():
	for entity_type, endpoint in [
		('Auto Tags', '/api/config/v1/autoTags'),
		('Host Conditional Naming Rules', '/api/config/v1/conditionalNaming/host'),
		('Process Group Conditional Naming Rules', '/api/config/v1/conditionalNaming/processGroup'),
		('Request Attributes', '/api/config/v1/service/requestAttributes'),
		('Request Naming Rules', '/api/config/v1/service/requestNaming'),
		('Service Conditional Naming Rules', '/api/config/v1/conditionalNaming/service'),
		('Dashboards', '/api/config/v1/dashboards'),
	]:
		report_fixed_id_entity(entity_type, endpoint)


def report_fixed_id_entity(entity_type, endpoint):
	print(f'{entity_type}:')
	print_lines = []
	r = get_object_list(endpoint)
	entity_json = json.loads(r.text)
	if endpoint == '/api/config/v1/dashboards':
		values_key = 'dashboards'
	else:
		values_key = 'values'
	entity_list = entity_json.get(values_key)
	for entity in entity_list:
		object_id = entity.get('id')
		name = entity.get('name')
		if is_fixed_id(object_id):
			print_lines.append(name + ': ' + object_id)

	for print_line in sorted(print_lines):
		print(print_line)


def is_fixed_id(entity_id):
	for fixed_id_startswith in fixed_id_startswith_list:
		if entity_id.startswith(fixed_id_startswith):
			return True

	return False


def get_object_list(endpoint: str) -> Response:
	url = env + endpoint
	try:
		r: Response = requests.get(url, params='', headers={'Authorization': 'Api-Token ' + token})
		if r.status_code not in [200]:
			print('Error in "get_object_list(endpoint)" method')
			print('Endpoint: ' + endpoint)
			print('Exit code shown below is the source code line number of the exit statement invoked')
			exit(get_line_number())
		return r
	except ssl.SSLError:
		print('SSL Error')
		exit(get_line_number())


def get_line_number():
	cf = currentframe()
	return cf.f_back.f_lineno


if __name__ == '__main__':
	process()
