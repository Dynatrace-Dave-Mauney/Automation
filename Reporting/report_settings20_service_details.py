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
	services_dicts = get_services(env, token)
	for services_dict in services_dicts:
		entity_id = services_dict.get('id')
		name = services_dict.get('name')
		# DEBUG: only process one Service
		# if 'TEMPLATE' in name:
		# if entity_id == 'APPLICATION-245DD7C386F6725E':
		summary.extend(process_service(env, token, summary_mode, entity_id, name, rows))

	if not summary_mode:
		report_name = 'Services Settings 2.0'
		report_writer.initialize_text_file(None)
		report_headers = ('Service Name', 'Entity ID', 'Schema ID', 'Value')
		report_writer.write_console(report_name, report_headers, rows, delimiter='|')
		report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
		write_strings(summary)
		report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
		report_writer.write_html(None, report_name, report_headers, rows)

	return summary


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


def process_service(env, token, summary_mode, entity_id, name, rows):
	summary = []

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

	for item in items:
		schema_id = item.get('schemaId')
		value = str(item.get('value'))
		value = value.replace('{', '')
		value = value.replace('}', '')
		value = value.replace("'", "")
		if not summary_mode:
			rows.append((name, entity_id, schema_id, value))

	return sorted(summary)


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
