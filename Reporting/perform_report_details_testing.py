#
# TODO:
# Configuration API:
# Remaining Anomaly Detection APIs
# Mobile Deobs: Need environment with it configured (Need API V1 Mobile symbolication file management)
#
# Environment V2:
# Davis Security Advisor: Need environment with it configured (Read security problems)
#
#
import sys
from datetime import date

# import report_activegate_details
# import report_alerting_profile_details
# import report_anomaly_detection_applications_details
# import report_anomaly_detection_database_services_details
# import report_anomaly_detection_disk_events_details
# import report_anomaly_detection_hosts_details
# import report_anomaly_detection_services_details
# import report_anomaly_detection_vmware_details
# import report_api_token_details
# import report_application_details
# import report_audit_log_details
# import report_autotag_details
# import report_aws_credential_details
# import report_aws_credential_details_specific_customer
# import report_azure_credential_details
# import report_calculated_metrics_details
# import report_cluster_details
# import report_conditional_naming_details
# import report_credential_vault_details
# import report_dashboard_details
# import report_data_privacy_details
# import report_extension_details
# import report_extension_v2_details
# import report_frequent_issue_detection_details
# import report_hosts_autoupdate_details
# import report_host_details
# import report_host_group_details
# import report_kubernetes_credential_details
# import report_maintenance_window_details
# import report_management_zone_details
# import report_mobile_application_details
# import report_network_zone_details
# import report_notification_details
# import report_oneagent_direct_communication_details
# import report_plugin_details
# import report_process_group_details
# import report_rum_details
# import report_service_details
# import report_service_settings_details
# import report_settings20_details
# import report_settings20_host_details
# import report_settings20_oneagent_features_details
# import report_settings20_process_group_details
# import report_settings20_service_details
# import report_settings20_web_application_details
# import report_synthetic_details
# import report_synthetic_http_check_details
# import report_synthetic_location_details
# import report_monitored_entities_custom_tags_details

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


def print_list(any_list):
	for line in any_list:
		line = line.replace('are 0', 'are no')
		line = line.replace('.  0 are', '.  None are')
		line = line.replace(' 0 are', ' none are')
		print(line)


def process():
	today = date.today()
	report_date = str(today.month) + '/' + str(today.day) + '/' + str(today.year)

	print('Report Details For ' + env_name + ' Environment As Of ' + report_date)

	# print('ActiveGate Summary')
	# report_activegate_details.process(env, token, True)
	# print_list(report_activegate_details.summarize(env, token))
	# # print('')
	#
	# print('Alerting Profiles Summary')
	# report_alerting_profile_details.process(env, token, True)
	# print_list(report_alerting_profile_details.summarize(env, token))
	# print('')
	#
	# print('Anomaly Detection For Applications Summary')
	# report_anomaly_detection_applications_details.process(env, token, True)
	# print_list(report_anomaly_detection_applications_details.summarize(env, token))
	# print('')
	#
	# print('Anomaly Detection For Database Services Summary')
	# report_anomaly_detection_database_services_details.process(env, token, True)
	# print_list(report_anomaly_detection_database_services_details.summarize(env, token))
	# print('')
	#
	# print('Anomaly Detection For Hosts Summary')
	# report_anomaly_detection_hosts_details.process(env, token, True)
	# print_list(report_anomaly_detection_hosts_details.summarize(env, token))
	# print('')
	#
	# print('Anomaly Detection For Services Summary')
	# report_anomaly_detection_services_details.process(env, token, True)
	# print_list(report_anomaly_detection_services_details.summarize(env, token))
	# print('')
	#
	# print('Anomaly Detection For VMWare Summary')
	# report_anomaly_detection_vmware_details.process(env, token, True)
	# print_list(report_anomaly_detection_vmware_details.summarize(env, token))
	# print('')
	#
	# print('Anomaly Detection For Disk Events Summary')
	# report_anomaly_detection_disk_events_details.process(env, token, True)
	# print_list(report_anomaly_detection_disk_events_details.summarize(env, token))
	# print('')
	#
	# print('API Token Summary')
	# report_api_token_details.process(env, token, True)
	# print_list(report_api_token_details.summarize(env, token))
	# print('')
	#
	# print('Applications (Web) Summary')
	# report_application_details.process(env, token, True)
	# print_list(report_application_details.summarize(env, token))
	# print('')
	#
	# print('Audit Log Summary')
	# report_audit_log_details.process(env, token, True)
	# print_list(report_audit_log_details.summarize(env, token))
	# print('')
	#
	# For raw json debug...
	# report_audit_log_details.process(env, token, False)

	# print('AutoTags Summary')
	# report_autotag_details.process(env, token, True)
	# print_list(report_autotag_details.summarize(env, token))
	# print('')
	#
	# print('AWS Configuration Summary')
	# report_aws_credential_details.process(env, token, True)
	# print_list(report_aws_credential_details.summarize(env, token))
	# print('')
	#
	# print('Azure Configuration Summary')
	# report_azure_credential_details.process(env, token, True)
	# print_list(report_azure_credential_details.summarize(env, token))
	# print('')
	#
	# print('Browser Synthetics Summary')
	# report_synthetic_details.process(env, token, True)
	# print_list(report_synthetic_details.summarize(env, token))
	# print('')
	#
	# print('Calculated Metrics Summary')
	# report_calculated_metrics_details.process(env, token, True)
	# print_list(report_calculated_metrics_details.summarize(env, token))
	# print('')
	#
	# print('Cluster Summary')
	# report_cluster_details.process(env, token, True)
	# print_list(report_cluster_details.summarize(env, token))
	# print('')
	#
	# print('Conditional Naming Summary')
	# report_conditional_naming_details.process(env, token, True)
	# print_list(report_conditional_naming_details.summarize(env, token))
	# print('')
	#
	# print('Credential Vault Summary')
	# report_credential_vault_details.process(env, token, True)
	# print_list(report_credential_vault_details.summarize(env, token))
	# print('')
	#
	# print('Dashboards Summary')
	# report_dashboard_details.process(env, token, True)
	# print_list(report_dashboard_details.summarize(env, token))
	# print('')
	#
	# print('Data Privacy Summary')
	# report_data_privacy_details.process(env, token, True)
	# print_list(report_data_privacy_details.summarize(env, token))
	# print('')
	#
	# print('Extension Summary')
	# report_extension_details.process(env, token, True)
	# print_list(report_extension_details.summarize(env, token))
	# print('')
	#
	# print('ExtensionV2 Summary')
	# report_extension_v2_details.process(env, token, True)
	# print_list(report_extension_v2_details.summarize(env, token))
	# print('')
	#
	# print('Frequent Issue Detection Summary')
	# report_frequent_issue_detection_details.process(env, token, True)
	# print_list(report_frequent_issue_detection_details.summarize(env, token))
	# print('')
	#
	# print('Hosts Summary')
	# report_host_details.process(env, token, True)
	# print_list(report_host_details.summarize(env, token))
	# print('')
	#
	# print('Host Groups Summary')
	# report_host_group_details.process(env, token, True)
	# print_list(report_host_group_details.summarize(env, token))
	# print('')
	#
	# print('OneAgent Auto Update Summary')
	# report_hosts_autoupdate_details.process(env, token, True)
	# print_list(report_hosts_autoupdate_details.summarize(env, token))
	# print('')
	#
	# print('HTTP Check Synthetics Summary')
	# report_synthetic_http_check_details.process(env, token, True)
	# print_list(report_synthetic_http_check_details.summarize(env, token))
	# print('')
	#
	# print('Kubernetes Configuration Summary')
	# report_kubernetes_credential_details.process(env, token, True)
	# print_list(report_kubernetes_credential_details.summarize(env, token))
	# print('')
	#
	# print('Maintenance Windows Summary')
	# report_maintenance_window_details.process(env, token, True)
	# print_list(report_maintenance_window_details.summarize(env, token))
	# print('')
	#
	# print('Management Zones Summary')
	# report_management_zone_details.process(env, token, True)
	# print_list(report_management_zone_details.summarize(env, token))
	# print('')
	#
	# print('Mobile Applications Summary')
	# report_mobile_application_details.process(env, token, True)
	# print_list(report_mobile_application_details.summarize(env, token))
	# print('')
	#
	# print('Network Zone Summary')
	# report_network_zone_details.process(env, token, True)
	# print_list(report_network_zone_details.summarize(env, token))
	# print('')
	#
	# print('Notifications Summary')
	# report_notification_details.process(env, token, True)
	# print_list(report_notification_details.summarize(env, token))
	# print('')
	#
	# print('OneAgents in Direct Communication Summary')
	# report_oneagent_direct_communication_details.process(env, token, True)
	# print_list(report_oneagent_direct_communication_details.summarize(env, token))
	# print('')
	#
	# print('Plugin Summary')
	# report_plugin_details.process(env, token, True)
	# print_list(report_plugin_details.summarize(env, token))
	# print('')
	#
	# print('Process Groups Summary')
	# report_process_group_details.process(env, token, True)
	# print_list(report_process_group_details.summarize(env, token))
	# print('')
	#
	# print('Services Summary')
	# report_service_details.process(env, token, True)
	# print_list(report_service_details.summarize(env, token))
	# print('')
	#
	# print('RUM Summary')
	# report_rum_details.process(env, token, True)
	# print_list(report_rum_details.summarize(env, token))
	# print('')
	#
	# print('Service Settings Summary')
	# report_service_settings_details.process(env, token, True)
	# print_list(report_service_settings_details.summarize(env, token))
	# print('')
	#
	# print('Settings 2.0 Summary')
	# report_settings20_details.process(env, token, True)
	# print_list(report_settings20_details.summarize(env, token))
	# print('')
	#
	# print('Settings 2.0 Web Applications Summary')
	# report_settings20_web_application_details.process(env, token, True)
	# print_list(report_settings20_web_application_details.summarize(env, token))
	# print('')
	#
	# print('Settings 2.0 Services Summary')
	# report_settings20_service_details.process(env, token, True)
	# print_list(report_settings20_service_details.summarize(env, token))
	# print('')
	#
	# print('Settings 2.0 Hosts Summary')
	# report_settings20_host_details.process(env, token, True)
	# print_list(report_settings20_host_details.summarize(env, token))
	# print('')
	#
	# print('Settings 2.0 OneAgent Features Summary')
	# report_settings20_oneagent_features_details.process(env, token, True)
	# print_list(report_settings20_oneagent_features_details.summarize(env, token))
	# print('')
	#
	# print('Settings 2.0 Process Groups Summary')
	# report_settings20_process_group_details.process(env, token, True)
	# print_list(report_settings20_host_details.summarize(env, token))
	# print('')
	#
	# print('Synthetic Location Summary')
	# report_synthetic_location_details.process(env, token, True)
	# print_list(report_synthetic_location_details.summarize(env, token))
	# print('')
	#
	#
	# Not (yet) part of the official report process
	#
	# print('Manual Tags')
	# report_monitored_entities_custom_tags_details.process(env, token, True)
	# print_list(report_monitored_entities_custom_tags_details.summarize(env, token))
	# print('')
	#
	# print('AWS Configuration Summary for specific customer')
	# report_aws_credential_details_specific_customer.process(env, token, True)
	# print_list(report_aws_credential_details_specific_customer.summarize(env, token))
	# print('')
	#


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
