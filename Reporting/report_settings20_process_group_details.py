import dynatrace_rest_api_helper
import os


def summarize(env, token):
	return process(env, token, False)


def get_process_groups(env, token):
	process_groups = []

	endpoint = '/api/v1/entity/infrastructure/process-groups'
	params = ''
	process_groups_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)
	for process_groups_json in process_groups_json_list:
		entity_id = process_groups_json.get('entityId')
		name = process_groups_json.get('displayName')
		process_groups.append({'id': entity_id, 'name': name})

	return process_groups


def process_process_group(entity_id, name, env, token, print_mode):
	summary = []
	findings = []

	endpoint = '/api/v2/settings/objects'
	# schemaIds = ['builtin:rum.web.request-errors', 'builtin:rum.web.enablement', 'builtin:preferences.privacy',
	# 			 'builtin:anomaly-detection.rum-web']
	# schema_id_param = 'schemaIds=' + str(schemaIds_param).replace("'", "").replace('[', '').replace(']','').replace(' ', '').replace(':', '%3A')
	# DEBUG: to show all schemas...
	schema_id_param = ''
	params = schema_id_param + '&scopes=' + entity_id + '&fields=schemaId%2Cvalue&pageSize=500'
	settings_object = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]
	items = settings_object.get('items', [])

	if items:
		if print_mode:
			print('process_group: ' + name)

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
			summary.append('process_group "' + name + '" findings:')
			summary.extend(findings)
		else:
			summary.append('process_group "' + name + '" has no findings')

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
	process_groups_dicts = get_process_groups(env, token)
	for process_groups_dict in process_groups_dicts:
		entity_id = process_groups_dict.get('id')
		name = process_groups_dict.get('name')
		# DEBUG: only process one process_group
		# if 'TEMPLATE' in name:
		# if entity_id == 'APPLICATION-245DD7C386F6725E':
		summary.extend(process_process_group(entity_id, name, env, token, print_mode))

	return summary


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
