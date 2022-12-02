import dynatrace_rest_api_helper
import os


def summarize(env, token):
	return process(env, token, False)


def process_oneagent_features(env, token, print_mode):
	summary = []
	# findings = []

	endpoint = '/api/v2/settings/objects'
	schema_id = ['builtin:oneagent.features']
	schema_id_param = 'schemaIds=' + str(schema_id).replace("'", "").replace('[', '').replace(']', '').replace(' ', '').replace(':', '%3A')
	params = schema_id_param + '&scopes=environment&fields=schemaId%2Cvalue%2CdisplayName&pageSize=500'
	settings_object = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]
	items = settings_object.get('items', [])

	lines = []

	if items:
		for item in items:
			# schema_id = item.get('schemaId')

			value = item.get('value')
			# enabled = value.get('enabled')
			# instrumentation = value.get('instrumentation', 'False')
			key = value.get('key')

			# value_string = str(value)
			# value_string = value_string.replace('{', '')
			# value_string = value_string.replace('}', '')
			# value_string = value_string.replace("'", "")

			if True:
				# if enabled == 'False':
				# lines.append(str(key) + ': ' + str(instrumentation))
				lines.append(str(key))

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
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, True)


if __name__ == '__main__':
    # print('Not to be run standalone.  Use one of the "perform_*.py" modules to run this module.')
    # exit(1)
    main()
