# Report changes made via automation:
# RobotAdmin
# Dashboards/Templates
# Dashboards/Sandbox)

import json

from Reuse import dynatrace_api
from Reuse import environment

friendly_function_name = 'Dynatrace Automation Tools'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Prod'
# env_name_supplied = 'NonProd'
# env_name_supplied = 'Prep'
# env_name_supplied = 'Dev'
# env_name_supplied = 'Personal'
# env_name_supplied = 'FreeTrial1'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

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
	r = dynatrace_api.get_object_list(env, token, endpoint)
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


if __name__ == '__main__':
	process()
