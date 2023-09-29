# Generate an ALLOW rule for every settings 2.0 schema id.

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
	schemas = []

	allow1 = 'ALLOW settings:schemas:read, settings:objects:read settings:objects:write WHERE settings:schemaId = "'
	allow2 = '";'

	endpoint = '/api/v2/settings/schemas'
	params = ''
	settings_json_list = dynatrace_api.get(env, token, endpoint, params)

	for settings_json in settings_json_list:
		inner_settings_json_list = settings_json.get('items')
		for inner_settings_json in inner_settings_json_list:
			schema_id = inner_settings_json.get('schemaId')
			schemas.append(schema_id)

	for schema in sorted(schemas):
		print(allow1 + schema + allow2)


def main():
	friendly_function_name = 'Dynatrace Automation Tools'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'NonProd'
	# env_name_supplied = 'Prep'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

	process(env, token)


if __name__ == '__main__':
	main()
