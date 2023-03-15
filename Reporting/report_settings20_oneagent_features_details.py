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
	# env_name, env, token = environment.get_environment('Prod')
	# env_name, env, token = environment.get_environment('Prep')
	# env_name, env, token = environment.get_environment('Dev')
	env_name, env, token = environment.get_environment('Personal')
	# env_name, env, token = environment.get_environment('FreeTrial1')

	process(env, token, True)


if __name__ == '__main__':
	main()
