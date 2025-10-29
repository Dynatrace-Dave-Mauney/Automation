from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
	return process_report(env, token)


def process_report(env, token):
	rows = []
	total_key_user_actions_count = 0

	mobile_applications_dicts = get_mobile_applications(env, token)
	for mobile_applications_dict in mobile_applications_dicts:
		entity_id = mobile_applications_dict.get('id')
		name = mobile_applications_dict.get('name')
		key_user_actions_count = get_key_user_actions_count(env, token, entity_id)
		rows.append((name, entity_id, key_user_actions_count))
		total_key_user_actions_count += key_user_actions_count

	rows = sorted(rows)
	report_name = 'Mobile Applications Settings'
	report_writer.initialize_text_file(None)
	report_headers = ('mobile Application Name', 'Entity ID', 'Key User Actions Defined')
	report_writer.write_console(report_name, report_headers, rows, delimiter='|')
	report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
	report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
	report_writer.write_html(None, report_name, report_headers, rows)

	print('Total Mobile Application User Actions Defined:', total_key_user_actions_count)

	
def get_mobile_applications(env, token):
	mobile_applications = []

	endpoint = '/api/config/v1/applications/mobile'
	mobile_applications_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
	for mobile_applications_json in mobile_applications_json_list:
		inner_mobile_applications_json_list = mobile_applications_json.get('values')
		for inner_mobile_applications_json in inner_mobile_applications_json_list:
			entity_id = inner_mobile_applications_json.get('id')
			name = inner_mobile_applications_json.get('name')
			mobile_applications.append({'id': entity_id, 'name': name})

	return mobile_applications


def get_key_user_actions_count(env, token, entity_id):
	endpoint = f'/api/config/v1/applications/mobile/{entity_id}/keyUserActions'
	r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
	mobile_application_key_user_actions = r.json()

	print(mobile_application_key_user_actions)

	key_user_actions_count = 0

	key_user_actions = mobile_application_key_user_actions.get('keyUserActions')
	if key_user_actions and len(key_user_actions) > 0:
		key_user_actions_count = len(key_user_actions)

	return key_user_actions_count


def write_strings(string_list):
	report_writer.write_console_plain_text(string_list)
	report_writer.write_plain_text(None, string_list)


def main():
	friendly_function_name = 'Dynatrace Automation Reporting'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'PreProd'
	# env_name_supplied = 'Sandbox'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
	process(env, token)
	
	
if __name__ == '__main__':
	main()
