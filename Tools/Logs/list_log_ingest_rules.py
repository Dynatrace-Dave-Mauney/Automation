import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
	count_total = 0

	schema_id = 'builtin:logmonitoring.log-storage-settings'
	endpoint = '/api/v2/settings/objects'
	raw_params = f'schemaIds={schema_id}&fields=value,scope,objectId&pageSize=500'
	params = urllib.parse.quote(raw_params, safe='/,&=')
	settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

	print('Name', 'Enabled', 'Scope')

	for settings_object in settings_object_list:
		# print(settings_object)
		items = settings_object.get('items')
		for item in items:
			object_id = item.get('objectId')
			scope = item.get('scope')
			value = item.get('value')
			config_item_title = value.get('config-item-title')
			enabled = value.get('enabled')

			# Print oddballs
			# if not config_item_title.startswith('[Built-in] ') and not config_item_title.startswith('DELETE '):
			# 	if not config_item_title.startswith('Include ') and not config_item_title.startswith('Exclude '):
			# 		print(config_item_title, enabled, scope)
			# 		count_total += 1

			# Print non-built-in rules, and rules not targeted for deletion already
			# if not config_item_title.startswith('[Built-in] ') and not config_item_title.startswith('DELETE '):
			# 	print(config_item_title, enabled, scope)
			# 	count_total += 1

			# Print all
			print(config_item_title, enabled, scope)
			# print(config_item_title, object_id)
			# print_object(env, token, endpoint, object_id)
			count_total += 1

	print(f'There are {count_total} log ingest rules currently defined.')


def print_object(env, token, endpoint, object_id):
	r = dynatrace_api.get_by_object_id(env, token, endpoint, object_id)
	print(r)


def main():
	friendly_function_name = 'Dynatrace Automation Reporting'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'PreProd'
	# env_name_supplied = 'Sandbox'
	# env_name_supplied = 'Dev'
	env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
	process(env, token)


if __name__ == '__main__':
	main()
