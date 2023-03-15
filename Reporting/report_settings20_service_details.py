import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
	return process(env, token, False)


def get_services(env, token):
	services = []

	endpoint = '/api/v1/entity/services'
	params = ''
	services_json_list = dynatrace_api.get(env, token, endpoint, params)
	for services_json in services_json_list:
		entity_id = services_json.get('entityId')
		name = services_json.get('displayName')
		services.append({'id': entity_id, 'name': name})

	return services


def process_service(entity_id, name, env, token, print_mode):
	summary = []
	findings = []

	endpoint = '/api/v2/settings/objects'
	# To filter by schema ids...
	# schema_ids = 'builtin:rum.web.request-errors,builtin:rum.web.enablement,builtin:preferences.privacy,builtin:anomaly-detection.rum-web'
	# schema_id_param = f'schemaIds={str(schema_ids)}'
	# To show all schemas...
	schema_id_param = ''
	raw_params = f'{schema_id_param}&scopes={entity_id}&fields=schemaId,value&pageSize=500'
	params = urllib.parse.quote(raw_params, '/,&=')
	settings_object = dynatrace_api.get(env, token, endpoint, params)[0]
	items = settings_object.get('items', [])

	if items:
		if print_mode:
			print('Service: ' + name)

		for item in items:
			schema_id = item.get('schemaId')
			value = str(item.get('value'))
			value = value.replace('{', '')
			value = value.replace('}', '')
			value = value.replace("'", "")
			if print_mode:
				print(schema_id + ': ' + value)
			add_findings(findings, schema_id, item)

	summary = sorted(summary)

	if len(items) > 0:
		if len(findings) > 0:
			summary.append('Service "' + name + '" findings:')
			summary.extend(findings)
		else:
			summary.append('Service "' + name + '" has no findings')

	if print_mode:
		# print('Total Schemas: ' + str(count_total))
		# print('')
		print_list(summary)

	return summary


def add_findings(findings, schema_id, item):
	value = item.get('value')

	if schema_id == 'builtin:rum.web.request-errors':
		if value.get('ignoreRequestErrorsInApdexCalculation') != 'True':
			findings.append('Ignore Request Errors In Apdex Calculation is off.')
	else:
		if schema_id == 'builtin:rum.web.enablement':
			if value.get('rum').get('enabled') is not True:
				findings.append('RUM is disabled.')
			else:
				if value.get('rum').get('costAndTrafficControl') > 75:
					findings.append('RUM is set to capture more than 75% of sessions.')
			if value.get('sessionReplay').get('enabled') is not True:
				findings.append('Session Replay is disabled.')
			else:
				if value.get('sessionReplay').get('costAndTrafficControl') > 75:
					findings.append('Session Replay is set to capture more than 75% of sessions.')
		else:
			if schema_id == 'builtin:preferences.privacy':
				if value.get('masking').get('ipAddressMaskingEnabled') is not False:
					findings.append('IP masking is enabled.')
			else:
				if schema_id == 'builtin:anomaly-detection.rum-web':
					if value.get('responseTime').get('enabled') is not True:
						findings.append('Anomaly detection for response time is disabled.')
					if value.get('errorRate').get('enabled') is not True:
						findings.append('Anomaly detection for error rate is disabled.')
					if value.get('trafficDrops').get('enabled') is not True:
						findings.append('Anomaly detection for traffic drops is disabled.')
					if value.get('trafficSpikes').get('enabled') is not True:
						findings.append('Anomaly detection for traffic spikes is disabled.')


def process(env, token, print_mode):
	summary = []
	services_dicts = get_services(env, token)
	for services_dict in services_dicts:
		entity_id = services_dict.get('id')
		name = services_dict.get('name')
		# DEBUG: only process one Service
		# if 'TEMPLATE' in name:
		# if entity_id == 'APPLICATION-245DD7C386F6725E':
		summary.extend(process_service(entity_id, name, env, token, print_mode))

	return summary


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
