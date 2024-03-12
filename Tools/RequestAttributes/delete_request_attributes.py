from Reuse import dynatrace_api
from Reuse import environment

endpoint = '/api/config/v1/service/requestAttributes'

retain_list = [
	'id(POST_PARAMETER)',
	'id(QUERY_PARAMETER)',
	'user(REQUEST_HEADER)',
	'user(REQUEST_HEADER)-alternateServiceCenter',
	'user(REQUEST_HEADER)-authorized',
	'user(REQUEST_HEADER)-currentLocationServiceCenter',
	'user(REQUEST_HEADER)-device',
	'user(REQUEST_HEADER)-employeeFullId',
	'user(REQUEST_HEADER)-employeeId',
	'user(REQUEST_HEADER)-employeeMenuId',
	'user(REQUEST_HEADER)-employeeName',
	'user(REQUEST_HEADER)-forkliftNumber',
	'user(REQUEST_HEADER)-ipAddress',
	'user(REQUEST_HEADER)-originServiceCenter',
	'user(REQUEST_HEADER)-supervisor',
	'user(REQUEST_HEADER)-tabletSerialNumber',
	'user(REQUEST_HEADER)-valid',
	'userid(QUERY_PARAMETER)',
	'username(POST_PARAMETER)',
	'username(QUERY_PARAMETER)'
	'username(SESSION_ATTRIBUTE)',
]

retain_list = [
	'id(SESSION_ATTRIBUTE)',
	'id(POST_PARAMETER)',
	'id(QUERY_PARAMETER)',
	'name(QUERY_PARAMETER)',
	'user(POST_PARAMETER)',
	'user(QUERY_PARAMETER)',
	'user(REQUEST_HEADER)',
	'username(QUERY_PARAMETER)',
	'username(SESSION_ATTRIBUTE)',
	'username(POST_PARAMETER)',
]


def process(env, token):
	delete_list = []

	request_attribute_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

	for request_attribute in request_attribute_list:
		# print(request_attribute)
		values = request_attribute.get('values')
		for value in values:
			entity_id = value.get('id')
			name = value.get('name')

			if entity_id.startswith('aaaaaaaa-bbbb-cccc-dddd-') and not entity_id.startswith('aaaaaaaa-bbbb-cccc-dddd-0'):
				if name not in retain_list:
					print(name, entity_id)
					delete_list.append((name, entity_id))

			# if name == 'eap-requestuuid':
			# 	delete_list.append((name, entity_id))

			# CLEANUP ALL NON-BUILT-IN NAMES
			# if not config_value_title.startswith('[Built-in] ') and not config_value_title.startswith('DELETE '):
			# 	delete_list.append((config_value_title, entity_id))

			# if config_value_title.startswith('Include ') or config_value_title.startswith('Exclude '):
			# 	delete_list.append((config_value_title, entity_id))

			# if config_value_title.startswith('DELETE '):
			# 	# print(config_value_title, enabled, scope, entity_id)
			# 	delete_list.append((config_value_title, entity_id))

			# CLEANUP NON-STANDARD NAMES
			# if not config_value_title.startswith('[Built-in] ') and not config_value_title.startswith('DELETE '):
			# 	if not config_value_title.startswith('Include ') and not config_value_title.startswith('Exclude '):
			# 		# print(config_value_title, enabled, scope, entity_id)
			# 		delete_list.append((config_value_title, entity_id))

			# FOR MORE COMPLETE CLEANUP ONLY!
			# if config_value_title.startswith('Exclude Hibernate') or config_value_title.startswith('Exclude INFO') or config_value_title.startswith('Exclude Nginx'):
			# 	# print(config_value_title, enabled, scope, entity_id)
			# 	delete_list.append((config_value_title, entity_id))
			#
			# if config_value_title.startswith('Exclude k8s') or config_value_title.startswith('Exclude log') or config_value_title.startswith('Exclude Log'):
			# 	# print(config_value_title, enabled, scope, entity_id)
			# 	delete_list.append((config_value_title, entity_id))
			#
			# if config_value_title.startswith('Include k8s') or config_value_title.startswith('Include log') or config_value_title.startswith('Include Log'):
			# 	# print(config_value_title, enabled, scope, entity_id)
			# 	delete_list.append((config_value_title, entity_id))

	delete_list = sorted(delete_list)
	delete_count = len(delete_list)

	if delete_count > 0:
		print(f'The following {delete_count} request attributes will be deleted:')
		for value in delete_list:
			value_name = value[0]
			value_id = value[1]
			print(f'{value_name} ({value_id})')

		msg = f'Proceed with deletion of the {delete_count} request attributes listed above?'
		proceed = input("%s (Y/n) " % msg).upper() == 'Y'

		if proceed:
			for value in delete_list:
				value_name = value[0]
				value_id = value[1]
				print(f'Deleting: {value_name} ({value_id})')
				delete_entity_id(env, token, value[1])


def delete_entity_id(env, token, entity_id):
	dynatrace_api.delete_object(f'{env}{endpoint}/{entity_id}', token)


def main():
	friendly_function_name = 'Dynatrace Automation Reporting'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'PreProd'
	# env_name_supplied = 'Sandbox'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
	process(env, token)


if __name__ == '__main__':
	main()
