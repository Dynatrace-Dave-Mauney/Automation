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
	hosts_dicts = get_hosts(env, token)
	for hosts_dict in hosts_dicts:
		entity_id = hosts_dict.get('id')
		name = hosts_dict.get('name')
		# DEBUG: only process one host
		# if 'TEMPLATE' in name:
		# if entity_id == 'APPLICATION-245DD7C386F6725E':
		summary.extend(process_host(env, token, summary_mode, entity_id, name, rows))

	if not summary_mode:
		rows = sorted(rows)
		report_name = 'Host Settings 2.0'
		report_writer.initialize_text_file(None)
		report_headers = ('Host Name', 'Entity ID', 'Schema ID', 'Value')
		report_writer.write_console(report_name, report_headers, rows, delimiter='|')
		report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
		write_strings(summary)
		report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
		report_writer.write_html(None, report_name, report_headers, rows)

	return summary


def get_hosts(env, token):
	hosts = []

	endpoint = '/api/v1/entity/infrastructure/hosts'
	hosts_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
	for hosts_json in hosts_json_list:
		entity_id = hosts_json.get('entityId')
		name = hosts_json.get('displayName')
		hosts.append({'id': entity_id, 'name': name})

	return hosts


def process_host(env, token, summary_mode, entity_id, name, rows):
	summary = []

	endpoint = '/api/v2/settings/objects'
	# To filter schemas...
	# schema_ids = 'builtin:anomaly-detection.infrastructure-hosts,builtin:rum.web.request-errors,builtin:rum.web.enablement,builtin:preferences.privacy,builtin:anomaly-detection.rum-web'
	# schema_ids_param = f'schemaIds={schema_ids}'
	# To show all schemas...
	schema_ids_param = ''
	raw_params = f'{schema_ids_param}&scopes={entity_id}&fields=schemaId,value&pageSize=500'
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

		summary = sorted(summary)

	return summary


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
