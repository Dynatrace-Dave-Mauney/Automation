import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

schema_id = 'builtin:logmonitoring.log-storage-settings'
endpoint = '/api/v2/settings/objects'


def process(env, token):
	print_list = []
	delete_list = []
	count_total = 0

	raw_params = f'schemaIds={schema_id}&fields=value,scope,objectId&pageSize=500'
	params = urllib.parse.quote(raw_params, safe='/,&=')
	settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

	print('Name', 'Enabled', 'Scope', 'ObjectID')

	for settings_object in settings_object_list:
		# print(settings_object)
		items = settings_object.get('items')
		for item in items:
			object_id = item.get('objectId')
			scope = item.get('scope')
			value = item.get('value')
			config_item_title = value.get('config-item-title')
			enabled = value.get('enabled')

			print_list.append(f'{config_item_title} {enabled} {scope} {object_id}')

			if config_item_title.startswith('Include ') or config_item_title.startswith('Exclude '):
				delete_list.append((config_item_title, object_id))

			# if config_item_title.startswith('DELETE '):
			# 	# print(config_item_title, enabled, scope, object_id)
			# 	delete_list.append((config_item_title, object_id))

			# CLEANUP NON-STANDARD NAMES
			# if not config_item_title.startswith('[Built-in] ') and not config_item_title.startswith('DELETE '):
			# 	if not config_item_title.startswith('Include ') and not config_item_title.startswith('Exclude '):
			# 		# print(config_item_title, enabled, scope, object_id)
			# 		delete_list.append((config_item_title, object_id))

			# FOR MORE COMPLETE CLEANUP ONLY!
			# if config_item_title.startswith('Exclude Hibernate') or config_item_title.startswith('Exclude INFO') or config_item_title.startswith('Exclude Nginx'):
			# 	# print(config_item_title, enabled, scope, object_id)
			# 	delete_list.append((config_item_title, object_id))
			#
			# if config_item_title.startswith('Exclude k8s') or config_item_title.startswith('Exclude log') or config_item_title.startswith('Exclude Log'):
			# 	# print(config_item_title, enabled, scope, object_id)
			# 	delete_list.append((config_item_title, object_id))
			#
			# if config_item_title.startswith('Include k8s') or config_item_title.startswith('Include log') or config_item_title.startswith('Include Log'):
			# 	# print(config_item_title, enabled, scope, object_id)
			# 	delete_list.append((config_item_title, object_id))

	delete_list = sorted(delete_list)
	delete_count = len(delete_list)

	if delete_count > 0:
		print(f'The following {delete_count} log ingest rules will be deleted:')
		for item in delete_list:
			item_name = item[0]
			item_id = item[1]
			print(f'{item_name} ({item_id})')

		msg = f'Proceed with deletion of the {delete_count} log ingest rules listed above?'
		proceed = input("%s (Y/n) " % msg).upper() == 'Y'

		if proceed:
			for item in delete_list:
				item_name = item[0]
				item_id = item[1]
				print(f'Deleting: {item_name} ({item_id})')
				delete_object_id(env, token, item[1])


def delete_object_id(env, token, object_id):
	dynatrace_api.delete_object(f'{env}{endpoint}/{object_id}', token)


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
