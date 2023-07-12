import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


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
	settings_object = dynatrace_api.get(env, token, endpoint, params)[0]
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

			# if enabled == 'False':
			if True:
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
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token, True)
    
    
if __name__ == '__main__':
	main()
