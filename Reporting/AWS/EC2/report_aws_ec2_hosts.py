import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
	rows = []
	raw_endpoint = '/api/v2/entities?pageSize=4000&from=now-5y&entitySelector=type(EC2_INSTANCE)&fields=fromRelationships.isAccessibleBy'
	endpoint = urllib.parse.quote(raw_endpoint, safe='/,&=?')
	r = dynatrace_api.get_object_list(env, token, endpoint)
	ec2_instance_json = json.loads(r.text)
	ec2_instance_list = ec2_instance_json.get('entities')
	for ec2_instance in ec2_instance_list:
		# print(ec2_instance)
		display_name = ec2_instance.get('displayName')
		if not display_name.startswith('UNKNOWN'):
			rows.append([display_name])

	rows = sorted(rows)
	report_name = 'EC2 Hosts'
	report_writer.initialize_text_file(None)
	report_headers = ['Display Name']
	report_writer.write_console(report_name, report_headers, rows, delimiter='|')
	report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
	report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
	report_writer.write_html(None, report_name, report_headers, rows)


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