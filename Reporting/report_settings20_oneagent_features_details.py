import dynatrace_rest_api_helper
import os
import urllib.parse


def summarize(env, token):
	return process(env, token, False)


def process_oneagent_features(env, token, print_mode):
	summary = []
	# findings = []

	endpoint = '/api/v2/settings/objects'
	schema_ids = 'builtin:oneagent.features'
	schema_ids_param = f'schemaIds={schema_ids}'
	raw_params = schema_ids_param + '&scopes=environment&fields=schemaId,value,Summary&pageSize=500'
	params = urllib.parse.quote(raw_params, safe='/,&=')
	settings_object = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]
	items = settings_object.get('items', [])

	lines = []

	if items:
		for item in items:
			value = item.get('value')
			summary = item.get('summary')
			enabled = value.get('enabled')

			# schema_id = item.get('schemaId')
			# instrumentation = value.get('instrumentation', 'False')
			# key = value.get('key')
			# value_string = str(value)
			# value_string = value_string.replace('{', '')
			# value_string = value_string.replace('}', '')
			# value_string = value_string.replace("'", "")

			if True:
			# if enabled == 'False':
				# lines.append(str(key) + ': ' + str(instrumentation))
				# lines.append(str(key))
				lines.append(f'{summary}:{enabled}')

	# if print_mode:
				# print(schemaId + ': ' + value_string)

			# add_findings(findings, schema_id, item, env, name)

	if print_mode:
		print_list(sorted(lines))

	summary = sorted(summary)

	# if len(findings) > 0:
	# 	summary.append('Web Application "' + name + '" findings:')
	# 	summary.extend(findings)
	# else:
	# 	summary.append('Web Application "' + name + '" has no findings')

	if print_mode:
		pass
		# print('Total Schemas: ' + str(count_total))
		# print('')
		# print_list(summary)

	return summary


def process(env, token, print_mode):
	return process_oneagent_features(env, token, print_mode)


def print_list(any_list):
	for line in any_list:
		line = line.replace('are 0', 'are no')
		print(line)


def main():
	# env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
	# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
	env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
	# env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')
	# env_name, tenant_key, token_key = ('FreeTrial1', 'FREETRIAL1_TENANT', 'ROBOT_ADMIN_FREETRIAL1_TOKEN')
	tenant = os.environ.get(tenant_key)
	token = os.environ.get(token_key)
	env = f'https://{tenant}.live.dynatrace.com'

	process(env, token, True)


if __name__ == '__main__':
	# print('Not to be run standalone.  Use one of the "perform_*.py" modules to run this module.')
	# exit(1)
	main()
