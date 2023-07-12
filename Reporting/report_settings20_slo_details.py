import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
	return process(env, token, False)


def process_slos(env, token, print_mode):

	summary = []

	count_total = 0

	endpoint = '/api/v2/settings/objects'
	schema_ids = 'builtin:monitoring.slo'
	schema_ids_param = f'schemaIds={schema_ids}'
	raw_params = schema_ids_param + '&scopes=environment&fields=schemaId,value,Summary&pageSize=500'
	params = urllib.parse.quote(raw_params, safe='/,&=')
	settings_object = dynatrace_api.get(env, token, endpoint, params)[0]
	items = settings_object.get('items', [])

	lines = []

	if items:
		if print_mode:
			print('Name|Summary|MetricName|MetricExpression|Enabled')

		for item in items:
			value = item.get('value')
			slo_summary = item.get('summary')
			name = value.get('name')
			metric_name = value.get('metricName')
			metric_expression = value.get('metricExpression')
			enabled = value.get('enabled')

			if True:
				lines.append(f'{name}|{slo_summary}|{metric_name}|{metric_expression}|{enabled}')

			count_total += 1

	if print_mode:
		print_list(sorted(lines))
		print(f'Total SLO definitions: {str(count_total)}')

	summary.append('There are ' + str(count_total) + ' SLOs currently defined.')

	return summary


def process(env, token, print_mode):
	return process_slos(env, token, print_mode)


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
