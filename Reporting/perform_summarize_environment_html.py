# TODO:
# Alerting Profiles: check naming standard
# Notification Integrations: check naming standard, check for one-to-one mapping to Alerting Profile by same name
# Move mobile application settings comment to mobile applications section
# Management Zones: report when there are no covered entities


import sys
from datetime import date
import findings_loader
import report_activegate_details
import report_alerting_profile_details
import report_anomaly_detection_applications_details
import report_anomaly_detection_database_services_details
import report_anomaly_detection_disk_events_details
import report_anomaly_detection_hosts_details
import report_anomaly_detection_services_details
import report_anomaly_detection_vmware_details
# import report_api_token_details
import report_api_token_extended_details
import report_application_details
import report_autotag_details
import report_aws_credential_details
import report_azure_credential_details
import report_broken_slo_metrics
import report_calculated_metrics_details
import report_cluster_details
import report_conditional_naming_details
import report_credential_vault_details
# import report_dashboard_details
import report_dashboard_extended_details
import report_data_privacy_details
import report_database_service_details
import report_extension_details
import report_extension_v2_details
import report_frequent_issue_detection_details
import report_host_details
import report_hosts_without_host_group
import report_hosts_without_management_zone
import report_host_group_details
import report_hosts_autoupdate_details
import report_kubernetes_credential_details
import report_maintenance_window_details
import report_management_zone_details
import report_mobile_application_details
import report_monitored_entities_custom_tags_details
import report_network_zone_details
import report_notification_details
import report_oneagent_details
import report_oneagent_direct_communication_details
import report_ongoing_problems
import report_plugin_details
import report_process_group_details
import report_request_attribute_details
import report_rum_details
import report_service_details
import report_service_settings_details
import report_settings20_cloud_application_workload_detection_details
import report_settings20_cloud_kubernetes_monitoring_details
# import report_settings20_details
import report_settings20_service_key_requests_details
import report_settings20_slo_details
import report_slo_dashboard_references
import report_synthetic_details
import report_synthetic_consumption
import report_synthetic_http_check_details
import report_synthetic_location_details

# from Reuse import dynatrace_api
from Reuse import environment

friendly_function_name = 'Dynatrace Automation Reporting'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Prod'
# env_name_supplied = 'NonProd'
# env_name_supplied = 'PreProd'
# env_name_supplied = 'Dev'
# env_name_supplied = 'Personal'
# env_name_supplied = 'Demo'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

#
# Access Token Scopes Required:
#
# API v2 scopes
# Read ActiveGates
# Read ActiveGate tokens
# Read API tokens
# Read audit logs
# Read entities
# Read events
# Read extension monitoring configurations
# Read extension environment configurations
# Read extensions
# Read metrics
# Read network zones
# Read problems
# Read releases
# Read settings
# Read SLO
# Read synthetic locations
#
# API v1 scopes
# Access problem and event feed, metrics, and topology
# Mobile symbolication file management
# Read configuration
# Read synthetic monitors, locations, and nodes
# Read credential vault entries
#
# curl -X POST "https://xxxxxxxx.live.dynatrace.com/api/v2/apiTokens" -H "accept: application/json; charset=utf-8" -H "Content-Type: application/json; charset=utf-8" -d "{\"name\":\"\",\"scopes\":[]}" -H "Authorization: Api-Token YYYYYYYY"
#


html_top = '''<html>
<body>
<pre>'''

html_bottom = '''</pre>
</body>
</html>'''

# outfile and findings are global for convenience.
# outfile_name = '../$Output/Reporting/Environment_Summary_For_' + env_name.replace(' ', '_') + '.html'
# outfile_name = 'Environment_Summary_For_' + env_name.replace(' ', '_') + '.html'
outfile_name = 'perform_summarize_environment_html_for_' + env_name.replace(' ', '_') + '.html'
outfile = open(outfile_name, 'w')
outfile.close()

findings = {}

# Default for Heading: True
write_heading_switch = True

# Default for Summary: True
write_summary_switch = True

# Default for Blank Line: True
write_blank_line_switch = True


def write_h1_heading(heading):
	if write_heading_switch:
		# DEBUG:
		# print('Printing h1 heading')
		outfile.write('<h1>' + heading + '</h1>')
		outfile.write('\n')


def write_h2_heading(heading):
	if write_heading_switch:
		# DEBUG:
		# print('Printing h2 heading')
		outfile.write('<h2>' + heading + '</h2>')
		outfile.write('\n')


def write_h3_heading(heading):
	if write_heading_switch:
		# DEBUG:
		# print('Printing heading')
		outfile.write('<h3>' + heading + '</h3>')
		outfile.write('\n')


def write_summary(func):
	if write_summary_switch:
		summary_list = func(env, token)
		write_summary_results(summary_list)


def write_summary_results(summary_list):
	if write_summary_switch:
		for line in summary_list:
			line = line.replace('are 0', 'are no')
			line = line.replace('.  0 are', '.  None are')
			line = line.replace(' 0 are', ' none are')
			outfile.write(line)
			outfile.write('\n')


def write_line(content):
	outfile.write(content)
	outfile.write('\n')


def write_blank_line():
	if write_blank_line_switch:
		# DEBUG:
		# print('Printing blank line')
		write_line('<br>')


def write_findings(heading):
	global findings
	finding_lines = findings.get(heading, [])
	for finding_line in finding_lines:
		outfile.write('<font color="red">')
		outfile.write(finding_line)
		outfile.write('</font>')


def process():
	global outfile_name
	global outfile
	global findings

	findings = findings_loader.get_findings_dictionary(env_name.replace(' ', '_'))
	# print(findings)

	with open(outfile_name, "w", encoding='utf8') as outfile:
		print(f'Writing HTML output to {outfile_name}')

		today = date.today()
		report_date = str(today.month) + '/' + str(today.day) + '/' + str(today.year)

		# Begin HTML formatting
		write_line(html_top)

		# Write the environment summary header
		write_h1_heading('Environment Summary For ' + env_name + ' Environment As Of ' + report_date)

		# Write the Architecture summary header
		write_h2_heading('Architecture/Platform Section')

		heading = 'Cluster Summary'
		write_h3_heading(heading)
		write_summary(report_cluster_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'ActiveGate Summary'
		write_h3_heading(heading)
		write_summary(report_activegate_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'OneAgents Summary'
		write_h3_heading(heading)
		write_summary(report_oneagent_details.summarize)
		write_summary(report_oneagent_direct_communication_details.summarize)
		write_summary(report_hosts_autoupdate_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Network Zone Summary'
		write_h3_heading(heading)
		write_summary(report_network_zone_details.summarize)
		write_blank_line()
		write_findings(heading)

		# Write the Topology Section header
		write_h2_heading('Topology Section')

		heading = 'Web Applications Summary'
		write_h3_heading(heading)
		write_summary(report_application_details.summarize)
		write_summary(report_rum_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Mobile Applications Summary'
		write_h3_heading(heading)
		write_summary(report_mobile_application_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Browser Synthetics Summary'
		write_h3_heading(heading)
		write_summary(report_synthetic_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'HTTP Check Synthetics Summary'
		write_h3_heading(heading)
		write_summary(report_synthetic_http_check_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Synthetic Consumption Summary'
		write_h3_heading(heading)
		write_summary(report_synthetic_consumption.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Synthetic Location Summary'
		write_h3_heading(heading)
		write_summary(report_synthetic_location_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Services Summary'
		write_h3_heading(heading)
		write_summary(report_service_details.summarize)
		write_summary(report_request_attribute_details.summarize)
		write_summary(report_database_service_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Process Groups Summary'
		write_h3_heading(heading)
		write_summary(report_process_group_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Hosts Summary'
		write_h3_heading(heading)
		write_summary(report_host_details.summarize)
		write_summary(report_hosts_without_host_group.summarize)
		write_summary(report_hosts_without_management_zone.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Host Groups Summary'
		write_h3_heading(heading)
		write_summary_results(report_host_group_details.summarize(env, token, perform_check_naming_standard=True))
		write_blank_line()
		write_findings(heading)

		# Write the Extensions/Plugins/Integrations summary header
		write_h2_heading('Extensions and Integrations Section')

		heading = 'Extension V2 Summary'
		write_h3_heading(heading)
		write_summary(report_extension_v2_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Extension V1 Summary'
		write_h3_heading(heading)
		write_summary(report_extension_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Plugin Summary'
		write_h3_heading(heading)
		write_summary(report_plugin_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'AWS Configuration Summary'
		write_h3_heading(heading)
		write_summary(report_aws_credential_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Azure Configuration Summary'
		write_h3_heading(heading)
		write_summary(report_azure_credential_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Kubernetes Configuration Summary'
		write_h3_heading(heading)
		write_summary(report_kubernetes_credential_details.summarize)
		write_summary(report_settings20_cloud_application_workload_detection_details.summarize)
		write_summary(report_settings20_cloud_kubernetes_monitoring_details.summarize)
		write_blank_line()
		write_findings(heading)

		# Write the Settings summary header
		write_h2_heading('Settings Section')

		heading = 'Management Zones Summary'
		write_h3_heading(heading)
		write_summary_results(report_management_zone_details.summarize(env, token, perform_check_naming_standard=True))
		write_blank_line()
		write_findings(heading)

		heading = 'AutoTags Summary'
		write_h3_heading(heading)
		write_summary(report_autotag_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Manual Tags Summary'
		write_h3_heading(heading)
		write_summary(report_monitored_entities_custom_tags_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Alerting Profiles Summary'
		write_h3_heading(heading)
		write_summary(report_alerting_profile_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Notifications Summary'
		write_h3_heading(heading)
		write_summary(report_notification_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Dashboards Summary'
		write_h3_heading(heading)
		# write_summary(report_dashboard_details.summarize)
		write_summary(report_dashboard_extended_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Service Settings Summary'
		write_h3_heading(heading)
		write_summary(report_service_settings_details.summarize)
		write_summary(report_settings20_service_key_requests_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Calculated Metrics Summary'
		write_h3_heading(heading)
		write_summary(report_calculated_metrics_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Conditional Naming Summary'
		write_h3_heading(heading)
		write_summary(report_conditional_naming_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Maintenance Windows Summary'
		write_h3_heading(heading)
		write_summary(report_maintenance_window_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Data Privacy Summary'
		write_h3_heading(heading)
		write_summary(report_data_privacy_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Frequent Issue Detection Summary'
		write_h3_heading(heading)
		write_summary(report_frequent_issue_detection_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Credential Vault Summary'
		write_h3_heading(heading)
		write_summary(report_credential_vault_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Anomaly Detection For Applications Summary'
		write_h3_heading(heading)
		write_summary(report_anomaly_detection_applications_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Anomaly Detection For Services Summary'
		write_h3_heading(heading)
		write_summary(report_anomaly_detection_services_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Anomaly Detection For Database Services Summary'
		write_h3_heading(heading)
		write_summary(report_anomaly_detection_database_services_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Anomaly Detection For Hosts Summary'
		write_h3_heading(heading)
		write_summary(report_anomaly_detection_hosts_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Anomaly Detection For Disk Events Summary'
		write_h3_heading(heading)
		write_summary(report_anomaly_detection_disk_events_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Anomaly Detection For VMWare Summary'
		write_h3_heading(heading)
		write_summary(report_anomaly_detection_vmware_details.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'SLO Summary'
		write_h3_heading(heading)
		write_summary(report_settings20_slo_details.summarize)
		write_summary(report_broken_slo_metrics.summarize)
		write_summary(report_slo_dashboard_references.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'Problems Summary'
		write_h3_heading(heading)
		write_summary(report_ongoing_problems.summarize)
		write_blank_line()
		write_findings(heading)

		heading = 'API Token Summary'
		write_h3_heading(heading)
		write_summary(report_api_token_extended_details.summarize)
		write_blank_line()
		write_findings(heading)

		# This part is having issues...
		# TODO: Fix it!
		# heading = 'Settings 2.0 Summary'
		# write_h3_heading(heading)
		# write_summary(report_settings20_details.summarize)
		# write_blank_line()
		# write_findings(heading)

		# Finish the HTML formatting
		write_line(html_bottom)


def main(arguments):
	# For convenience, the default values are global and can be used easily
	# in the IDE or by passing no arguments from the command line.
	# Override them via command line by supplying the arguments.
	global env
	global token
	global env_name

	usage = '''
	perform_summarize_environment_print.py: Report environment summary

	Usage:    	perform_summarize_environment_print.py <tenant/environment URL> <token> <friendly_environment_name>
	Examples: 	perform_summarize_environment_print.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123 SaaSDemo
				perform_summarize_environment_print.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123 ManagedDemo
	'''

	# When no arguments are supplied, use the default global values
	if len(arguments) == 1:
		process()
		exit()

	if len(arguments) < 2:
		print(usage)
		raise ValueError('Too few arguments!')
	if len(arguments) > 4:
		print(help)
		raise ValueError('Too many arguments!')
	if arguments[1] in ['-h', '--help']:
		print(help)
	elif arguments[1] in ['-v', '--version']:
		print('1.0')
	else:
		if len(arguments) == 4:
			# Override the default global values when arguments are supplied
			env = arguments[1]
			token = arguments[2]
			env_name = arguments[3]
			process()
		else:
			print(usage)
			raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
	main(sys.argv)
