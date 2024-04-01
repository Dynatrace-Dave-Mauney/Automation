from Reuse import dynatrace_api
from Reuse import environment

endpoint = f'/api/config/v1/autoTags'

retain_list = [
	'Geolocation',
]


def process(env, token):
	delete_list = []

	auto_tag_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

	for auto_tag in auto_tag_list:
		# print(auto_tag)
		values = auto_tag.get('values')
		for value in values:
			entity_id = value.get('id')
			name = value.get('name')
			# print(entity_id, name)

			if entity_id.startswith('aaaaaaaa-bbbb-cccc-dddd-'):
				if name not in retain_list:
					print(name, entity_id)
					delete_list.append((name, entity_id))

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
	env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
	process(env, token)


if __name__ == '__main__':
	main()
