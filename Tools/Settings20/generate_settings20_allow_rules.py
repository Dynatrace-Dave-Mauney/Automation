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
	# env_name, env, token = environment.get_environment('Prod')
	# env_name, env, token = environment.get_environment('Prep')
	# env_name, env, token = environment.get_environment('Dev')
	env_name, env, token = environment.get_environment('Personal')
	# env_name, env, token = environment.get_environment('FreeTrial1')

	process(env, token)


if __name__ == '__main__':
	main()
