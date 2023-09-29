import sys
from datetime import date
import report_activegate_details
import report_alerting_profile_details
import report_anomaly_detection_applications_details
import report_anomaly_detection_database_services_details
import report_anomaly_detection_disk_events_details
import report_anomaly_detection_hosts_details
import report_anomaly_detection_services_details
import report_anomaly_detection_vmware_details
import report_api_token_details
import report_application_details
import report_autotag_details
import report_aws_credential_details
import report_azure_credential_details
import report_calculated_metrics_details
# import report_cluster_details
import report_conditional_naming_details
import report_credential_vault_details
import report_dashboard_details
import report_data_privacy_details
import report_extension_details
import report_extension_v2_details
import report_frequent_issue_detection_details
import report_host_details
import report_host_group_details
import report_kubernetes_credential_details
import report_maintenance_window_details
import report_management_zone_details
import report_mobile_application_details
import report_network_zone_details
import report_notification_details
import report_plugin_details
import report_process_group_details
import report_service_details
import report_service_settings_details
import report_settings20_details
import report_synthetic_details
import report_synthetic_http_check_details
import report_synthetic_location_details

from Reuse import environment

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

# Default for Heading: True
print_heading_switch = True

# Default for Details: False
print_details_switch = False

# Default for Summary: True (if details is True, usually this should be false to avoid duplication)
print_summary_switch = True

# Default for Blank Line: True
print_blank_line_switch = True


def print_heading(heading):
	if print_heading_switch:
		# DEBUG:
		# print('Printing heading')
		print(heading)


def print_details(func):
	if print_details_switch:
		# DEBUG:
		# print('Printing details')
		func(env, token, True)


def print_summary(func):
	if print_summary_switch:
		# DEBUG:
		# print('Printing summary')
		summary_list = func(env, token)
		for line in summary_list:
			line = line.replace('are 0', 'are no')
			line = line.replace('.  0 are', '.  None are')
			line = line.replace(' 0 are', ' none are')
			print(line)


def print_blank_line():
	if print_blank_line_switch:
		# DEBUG:
		# print('Printing blank line')
		pass
	print('')


def process():
	today = date.today()
	report_date = str(today.month) + '/' + str(today.day) + '/' + str(today.year)

	# Print the environment summary header
	print_heading('Environment Summary For ' + env_name + ' as of ' + report_date)

	# Print the Architecture summary header
	print_heading('Architecture')

	# MAYBE OBSOLETE?
	# print_heading('Cluster Summary')
	# print_details(report_cluster_details.process)
	# print_summary(report_cluster_details.summarize)
	# print_blank_line()
	#
	print_heading('ActiveGate Summary')
	print_details(report_activegate_details.process)
	print_summary(report_activegate_details.summarize)
	print_blank_line()

	print_heading('Synthetic Location Summary')
	print_details(report_synthetic_location_details.process)
	print_summary(report_synthetic_location_details.summarize)
	print_blank_line()

	print_heading('Network Zone Summary')
	print_details(report_network_zone_details.process)
	print_summary(report_network_zone_details.summarize)
	print_blank_line()

	# Print the Topology summary header
	print_heading('Topology')

	print_heading('Applications (Web) Summary')
	print_details(report_application_details.process)
	print_summary(report_application_details.summarize)
	print_blank_line()

	print_heading('Mobile Applications Summary')
	print_details(report_mobile_application_details.process)
	print_summary(report_mobile_application_details.summarize)
	print_blank_line()

	print_heading('Browser Synthetics Summary')
	print_details(report_synthetic_details.process)
	print_summary(report_synthetic_details.summarize)
	print_blank_line()

	print_heading('HTTP Check Synthetics Summary')
	print_details(report_synthetic_http_check_details.process)
	print_summary(report_synthetic_http_check_details.summarize)
	print_blank_line()

	print_heading('Services Summary')
	print_details(report_service_details.process)
	print_summary(report_service_details.summarize)
	print_blank_line()

	print_heading('Process Groups Summary')
	print_details(report_process_group_details.process)
	print_summary(report_process_group_details.summarize)
	print_blank_line()

	print_heading('Hosts Summary')
	print_details(report_host_details.process)
	print_summary(report_host_details.summarize)
	print_blank_line()

	print_heading('Host Groups Summary')
	print_details(report_host_group_details.process)
	print_summary(report_host_group_details.summarize)
	print_blank_line()

	print_heading('Extension Summary')
	print_details(report_extension_details.process)
	print_summary(report_extension_details.summarize)
	print_blank_line()

	print_heading('ExtensionV2 Summary')
	print_details(report_extension_v2_details.process)
	print_summary(report_extension_v2_details.summarize)
	print_blank_line()

	print_heading('Plugin Summary')
	print_details(report_plugin_details.process)
	print_summary(report_plugin_details.summarize)
	print_blank_line()

	print_heading('AWS Configuration Summary')
	print_details(report_aws_credential_details.process)
	print_summary(report_aws_credential_details.summarize)
	print_blank_line()

	print_heading('Azure Configuration Summary')
	print_details(report_azure_credential_details.process)
	print_summary(report_azure_credential_details.summarize)
	print_blank_line()

	print_heading('Kubernetes Configuration Summary')
	print_details(report_kubernetes_credential_details.process)
	print_summary(report_kubernetes_credential_details.summarize)
	print_blank_line()

	# Print the Settings summary header
	print_heading('Settings')

	print_heading('Management Zones Summary')
	print_details(report_management_zone_details.process)
	print_summary(report_management_zone_details.summarize)
	print_blank_line()

	print_heading('AutoTags Summary')
	print_details(report_autotag_details.process)
	print_summary(report_autotag_details.summarize)
	print_blank_line()

	print_heading('Alerting Profiles Summary')
	print_details(report_alerting_profile_details.process)
	print_summary(report_alerting_profile_details.summarize)
	print_blank_line()

	print_heading('Notifications Summary')
	print_details(report_notification_details.process)
	print_summary(report_notification_details.summarize)
	print_blank_line()

	print_heading('Dashboards Summary')
	print_details(report_dashboard_details.process)
	print_summary(report_dashboard_details.summarize)
	print_blank_line()

	print_heading('Service Settings Summary')
	print_details(report_service_settings_details.process)
	print_summary(report_service_settings_details.summarize)
	print_blank_line()

	print_heading('Calculated Metrics Summary')
	print_details(report_calculated_metrics_details.process)
	print_summary(report_calculated_metrics_details.summarize)
	print_blank_line()

	print_heading('Conditional Naming Summary')
	print_details(report_conditional_naming_details.process)
	print_summary(report_conditional_naming_details.summarize)
	print_blank_line()

	print_heading('Maintenance Windows Summary')
	print_details(report_maintenance_window_details.process)
	print_summary(report_maintenance_window_details.summarize)
	print_blank_line()

	print_heading('Data Privacy Summary')
	print_details(report_data_privacy_details.process)
	print_summary(report_data_privacy_details.summarize)
	print_blank_line()

	print_heading('Frequent Issue Detection Summary')
	print_details(report_frequent_issue_detection_details.process)
	print_summary(report_frequent_issue_detection_details.summarize)
	print_blank_line()

	print_heading('Credential Vault Summary')
	print_details(report_credential_vault_details.process)
	print_summary(report_credential_vault_details.summarize)
	print_blank_line()

	print_heading('Anomaly Detection For Applications Summary')
	print_details(report_anomaly_detection_applications_details.process)
	print_summary(report_anomaly_detection_applications_details.summarize)
	print_blank_line()

	print_heading('Anomaly Detection For Services Summary')
	print_details(report_anomaly_detection_services_details.process)
	print_summary(report_anomaly_detection_services_details.summarize)
	print_blank_line()

	print_heading('Anomaly Detection For Database Services Summary')
	print_details(report_anomaly_detection_database_services_details.process)
	print_summary(report_anomaly_detection_database_services_details.summarize)
	print_blank_line()

	print_heading('Anomaly Detection For Hosts Summary')
	print_details(report_anomaly_detection_hosts_details.process)
	print_summary(report_anomaly_detection_hosts_details.summarize)
	print_blank_line()

	print_heading('Anomaly Detection For VMWare Summary')
	print_details(report_anomaly_detection_vmware_details.process)
	print_summary(report_anomaly_detection_vmware_details.summarize)
	print_blank_line()

	print_heading('Anomaly Detection For Disk Events Summary')
	print_details(report_anomaly_detection_disk_events_details.process)
	print_summary(report_anomaly_detection_disk_events_details.summarize)
	print_blank_line()

	print_heading('API Token Summary')
	print_details(report_api_token_details.process)
	print_summary(report_api_token_details.summarize)
	print_blank_line()

	print_heading('Settings 2.0 Summary')
	print_details(report_settings20_details.process)
	print_summary(report_settings20_details.summarize)
	print_blank_line()


def main(arguments):
	# For convenience, the default values are global and can be used easily
	# in the IDE or by passing no arguments from the command line.
	# Override them via command line by supplying the arguments.
	global env
	global token
	global env_name

	usage = '''
	perform_summarize_environment_print.py: Report environment summary
	 
	Usage:    perform_summarize_environment_print.py <tenant/environment URL> <token> <friendly_environment_name>
	Examples: perform_summarize_environment_print.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123 SaaSDemo
			  perform_summarize_environment_print.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123 ManagedDemo
	'''

	# DEBUG:
	# print('main invoked')
	# print('args' + str(arguments))
	# print(env)

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

