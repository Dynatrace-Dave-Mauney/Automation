import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
	return process_report(env, token, True)


def process(env, token):
	return process_report(env, token, False)


def process_report(env, token, summary_mode):
	rows = []
	summary = []
	web_applications_dicts = get_web_applications(env, token)
	for web_applications_dict in web_applications_dicts:
		entity_id = web_applications_dict.get('id')
		name = web_applications_dict.get('name')

		if 'PRD' not in name.upper():
			continue

		# DEBUG: only process one web application
		# if 'TEMPLATE' in name:
		# if entity_id == 'APPLICATION-245DD7C386F6725E':
		summary.extend(process_web_application(env, token, summary_mode, entity_id, name, rows))

	if not summary_mode:
		rows = sorted(rows)
		report_name = 'Web Applications Settings 2.0'
		report_writer.initialize_text_file(None)
		report_headers = ('Web Application Name', 'Entity ID', 'Schema ID', 'Value')
		report_writer.write_console(report_name, report_headers, rows, delimiter='|')
		report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
		write_strings(summary)
		report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
		report_writer.write_html(None, report_name, report_headers, rows)

	return summary


def get_web_applications(env, token):
	web_applications = []

	endpoint = '/api/config/v1/applications/web'
	web_applications_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
	for web_applications_json in web_applications_json_list:
		inner_web_applications_json_list = web_applications_json.get('values')
		for inner_web_applications_json in inner_web_applications_json_list:
			entity_id = inner_web_applications_json.get('id')
			name = inner_web_applications_json.get('name')
			web_applications.append({'id': entity_id, 'name': name})

	return web_applications


def process_web_application(env, token, summary_mode, entity_id, name, rows):
	summary = []
	# findings = []

	endpoint = '/api/v2/settings/objects'
	schema_id_list = 'builtin:rum.web.request-errors,builtin:rum.web.enablement,builtin:preferences.privacy,builtin:anomaly-detection.rum-web'
	schema_id_param = f'schemaIds={schema_id_list}'
	# DEBUG: to show all schemas...
	# schema_id_param = ''
	raw_params = f'{schema_id_param}&scopes={entity_id}&fields=schemaId,value&pageSize=500'
	params = urllib.parse.quote(raw_params, safe='/,&=')
	settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

	for settings_object in settings_object_list:
		items = settings_object.get('items', [])

		for item in items:
			schema_id = item.get('schemaId')
			value = str(item.get('value'))
			value = value.replace('{', '')
			value = value.replace('}', '')
			value = value.replace("'", "")
			if not summary_mode:
				rows.append((name, entity_id, schema_id, value))
			# add_findings(findings, schema_id, item)

		summary = sorted(summary)

	# if len(findings) > 0:
	# 	summary.append('Web Application "' + name + '" findings:')
	# 	summary.extend(findings)
	# else:
	# 	summary.append('Web Application "' + name + '" has no findings')

	return summary


# def add_findings(findings, schema_id, item):
# 	value = item.get('value')
# 
# 	if schema_id == 'builtin:rum.web.request-errors':
# 		if value.get('ignoreRequestErrorsInApdexCalculation') != 'True':
# 			findings.append('Ignore Request Errors In Apdex Calculation is off.')
# 	else:
# 		if schema_id == 'builtin:rum.web.enablement':
# 			if value.get('rum').get('enabled') is not True:
# 				findings.append('RUM is disabled.')
# 			else:
# 				if value.get('rum').get('costAndTrafficControl') > 75:
# 					findings.append('RUM is set to capture more than 75% of sessions.')
# 			if value.get('sessionReplay').get('enabled') is not True:
# 				findings.append('Session Replay is disabled.')
# 			else:
# 				if value.get('sessionReplay').get('costAndTrafficControl') > 75:
# 					findings.append('Session Replay is set to capture more than 75% of sessions.')
# 		else:
# 			if schema_id == 'builtin:preferences.privacy':
# 				if value.get('masking').get('ipAddressMaskingEnabled') is not False:
# 					findings.append('IP masking is enabled.')
# 			else:
# 				if schema_id == 'builtin:anomaly-detection.rum-web':
# 					if value.get('responseTime').get('enabled') is not True:
# 						findings.append('Anomaly detection for response time is disabled.')
# 					if value.get('errorRate').get('enabled') is not True:
# 						findings.append('Anomaly detection for error rate is disabled.')
# 					if value.get('trafficDrops').get('enabled') is not True:
# 						findings.append('Anomaly detection for traffic drops is disabled.')
# 					if value.get('trafficSpikes').get('enabled') is not True:
# 						findings.append('Anomaly detection for traffic spikes is disabled.')


def write_strings(string_list):
	report_writer.write_console_plain_text(string_list)
	report_writer.write_plain_text(None, string_list)


def main():
	friendly_function_name = 'Dynatrace Automation Reporting'
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
