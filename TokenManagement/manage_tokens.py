import json

from Reuse import dynatrace_api
from Reuse import environment

friendly_function_name = 'Dynatrace Automation Token Management'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Sandbox'
# env_name_supplied = 'PreProd'
# env_name_supplied = 'Prod'
# env_name_supplied = 'Personal'
# env_name_supplied = 'Demo'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

endpoint = '/api/v2/apiTokens'


def process():
	if not env or not token:
		print('Env or Token Environment Variable Not Set!')
		exit(1)

	# Run test
	# test()

	# or...

	# Create some tokens!
	# These are the most important ones for the "Automation" project...
	# post_reduced_power_dynatrace_automation_token()
	# post_saas_upgrade_assisant_token()
	# post_dynatrace_automation_token()
	# post_reporting_token()
	# post_tools_token()

	# These are important for other reasons
	# post_monaco_token()
	# post_installer_download_token()

	# These are more "special cases"
	# post_slo_generation_token()
	# post_fargate_paas_plus_token()
	# post_fargate_paas_token()
	# post_active_gate_certificate_management_token()

	# Commonly used for obvious reasons
	# list_tokens()

	# See "test()" method for common examples, if you don't see it above...

	# Current Customer
	# post_monaco_token()
	# post_read_metrics_token()



def post_api_token():
	return post_token('API Tokens (Read/Write)', ["apiTokens.read", "apiTokens.write"])


def post_reduced_power_dynatrace_automation_token():
	# Supports Token Key: DYNATRACE_AUTOMATION_PERSONAL_TOKEN (where "PERSONAL" can be any environment name).
	# Has every known permission needed by the automation project (and maybe some more!)
	return post_token('Automation', [
		"DTAQLAccess",
		"DataExport",
		"DssFileManagement",
		"ReadConfig",
		"ReadSyntheticData",
		"RumJavaScriptTagManagement",
		"WriteConfig",
		"activeGateTokenManagement.read",
		"activeGates.read",
		"apiTokens.read",
		"auditLogs.read",
		"credentialVault.read",
		"entities.read",
		"entities.write",
		"events.ingest",
		"events.read",
		"events.read",
		"extensionConfigurations.read",
		"extensionEnvironment.read",
		"extensions.read",
		"geographicRegions.read",
		"hub.read",
		"logs.ingest",
		"metrics.ingest",
		"metrics.read",
		"networkZones.read",
		"problems.read",
		"releases.read",
		"settings.read",
		"settings.write",
		"slo.read",
		"slo.write",
		"syntheticExecutions.read",
		"syntheticLocations.read",
		])


def post_dynatrace_automation_token():
	# Supports Token Key: DYNATRACE_AUTOMATION_PERSONAL_TOKEN (where "PERSONAL" can be any environment name).
	# Has every known permission needed by the automation project (and maybe some more!)
	return post_token('Automation', [
		"ActiveGateCertManagement",
		"CaptureRequestData",
		"DTAQLAccess",
		"DataExport",
		"DataImport",
		"DssFileManagement",
		"ExternalSyntheticIntegration",
		"InstallerDownload",
		"ReadConfig",
		"ReadSyntheticData",
		"RumJavaScriptTagManagement",
		"WriteConfig",
		"activeGateTokenManagement.read",
		"activeGates.read",
		"apiTokens.read",
		"auditLogs.read",
		"credentialVault.read",
		"entities.read",
		"entities.write",
		"events.ingest",
		"events.read",
		"events.read",
		"extensionConfigurations.read",
		"extensionEnvironment.read",
		"extensions.read",
		"geographicRegions.read",
		"hub.read",
		"logs.ingest",
		"metrics.ingest",
		"metrics.read",
		"networkZones.read",
		"problems.read",
		"releases.read",
		"settings.read",
		"settings.write",
		"slo.read",
		"slo.write",
		"syntheticExecutions.read",
		"syntheticLocations.read",
		])


def post_saas_upgrade_assisant_token():
	return post_token('SaaS Upgrade Assistant', [
		"networkZones.read",
		"networkZones.write",
		"settings.read",
		"settings.write",
		"slo.read",
		"slo.write",
		"CaptureRequestData",
		"DataExport",
		"ExternalSyntheticIntegration",
		"ReadConfig",
		"WriteConfig",
	])

def post_reporting_token():
	return post_token('Automation Reporting', ["activeGates.read", "activeGateTokenManagement.read", "apiTokens.read", "auditLogs.read", "entities.read", "events.read", "extensionConfigurations.read", "extensionEnvironment.read", "extensions.read", "metrics.read", "networkZones.read", "problems.read", "releases.read", "settings.read", "slo.read", "syntheticLocations.read", "credentialVault.read", "DataExport", "DssFileManagement", "ReadConfig", "ReadSyntheticData"])
	# return post_token('Reporting Pipeline', ["activeGates.read", "activeGateTokenManagement.read", "apiTokens.read", "auditLogs.read", "entities.read", "events.read", "extensionConfigurations.read", "extensionEnvironment.read", "extensions.read", "metrics.read", "networkZones.read", "problems.read", "releases.read", "settings.read", "slo.read", "syntheticLocations.read", "credentialVault.read", "DataExport", "DssFileManagement", "ReadConfig", "ReadSyntheticData"])


def post_tools_token():
	return post_token('Automation Tools', ["activeGates.read", "activeGateTokenManagement.read", "apiTokens.read", "auditLogs.read", "credentialVault.read", "entities.read", "entities.write", "events.ingest", "events.read", "extensionConfigurations.read", "extensionEnvironment.read", "extensions.read", "geographicRegions.read", "hub.read", "metrics.read", "networkZones.read", "problems.read", "releases.read", "settings.read", "settings.write", "slo.read", "syntheticExecutions.read", "syntheticLocations.read", "CaptureRequestData", "DataExport", "DataImport", "DssFileManagement", "DTAQLAccess", "ExternalSyntheticIntegration", "LogExport", "ReadConfig", "ReadSyntheticData", "WriteConfig"])


def post_tools_token_without_log_export():
	return post_token('Automation Tools', ["activeGates.read", "activeGateTokenManagement.read", "apiTokens.read", "auditLogs.read", "credentialVault.read", "entities.read", "entities.write", "events.ingest", "events.read", "extensionConfigurations.read", "extensionEnvironment.read", "extensions.read", "geographicRegions.read", "hub.read", "metrics.read", "networkZones.read", "problems.read", "releases.read", "settings.read", "settings.write", "slo.read", "syntheticExecutions.read", "syntheticLocations.read", "CaptureRequestData", "DataExport", "DataImport", "DssFileManagement", "DTAQLAccess", "ExternalSyntheticIntegration", "ReadConfig", "ReadSyntheticData", "WriteConfig"])


def post_dashboard_generator_token():
	return post_token('Dashboard Generator', ["metrics.read", "ReadConfig", "WriteConfig"])


def post_esa_token():
	return post_token('ESA', ["activeGates.read", "auditLogs.read", "entities.read", "events.read", "extensionConfigurations.read", "extensionEnvironment.read", "extensions.read", "geographicRegions.read", "metrics.read", "networkZones.read", "problems.read", "settings.read", "slo.read", "syntheticLocations.read", "DataExport", "DTAQLAccess", "ReadConfig", "ReadSyntheticData"])


def post_logs_ingest_token():
	return post_token('Logs Ingest', ["logs.ingest"])


def post_monaco_token():
	# Full Permissions
	# return post_token('Monaco', ["entities.read", "settings.read", "settings.write", "slo.read", "credentialVault.read", "DataExport", "ReadConfig", "ReadSyntheticData", "WriteConfig", "CaptureRequestData"])

	# Customer-specific Permissions
	return post_token('Monaco', ["entities.read", "settings.read", "settings.write", "slo.read", "credentialVault.read", "DataExport", "ReadConfig", "ReadSyntheticData", "WriteConfig"])


def post_fargate_paas_token():
	# https://www.dynatrace.com/support/help/shortlink/aws-fargate#prerequisites
	# Access problem and event feed, metrics, and topology (API v1)
	# PaaS integration - Installer download
	return post_token('Fargate PaaS with Jenkins', ["DataExport", "InstallerDownload"])


def post_fargate_paas_plus_token():
	return post_token('Fargate PaaS Plus', ["DataExport", "InstallerDownload", "events.ingest", "RumJavaScriptTagManagement", "ReadConfig", "WriteConfig"])


def post_installer_download_token():
	return post_token('InstallerDownload', ["InstallerDownload"])


def post_active_gate_certificate_management_token():
	return post_token('ActiveGate Certificate Management', ["ActiveGateCertManagement"])


def post_mute_tenable_token():
	return post_token('Mute Tenable', ["entities.read", "settings.read", "settings.write"])


def post_problem_analysis_token():
	return post_token('Problem Analysis', ["metrics.read", "problems.read", "settings.read"])


def post_read_metrics_token():
	return post_token('Read Metrics', ["metrics.read"])


def post_super_reader_token():
	# Without Log Access since my user does not have that permission
	return post_token('Super Reader', ["activeGates.read", "activeGateTokenManagement.read", "apiTokens.read", "entities.read", "events.read", "extensionConfigurations.read", "extensionEnvironment.read", "extensions.read", "geographicRegions.read", "hub.read", "metrics.read", "networkZones.read", "problems.read", "releases.read", "settings.read", "slo.read", "syntheticExecutions.read", "syntheticLocations.read", "credentialVault.read", "DataExport", "DataImport", "ExternalSyntheticIntegration", "ReadConfig", "ReadSyntheticData"])


def post_terraform_read_token():
	return post_token('Terraform Read', ["settings.read", "slo.read", "CaptureRequestData", "ExternalSyntheticIntegration", "ReadConfig"])


def post_slo_generation_token():
	return post_token('SLO Generation Pipeline', ["entities.read", "ReadConfig", "WriteConfig", "settings.read", "settings.write",  "slo.read",  "slo.write"])


def post_test_token():
	return post_token('Test', ["ReadConfig"])


def post_token(token_name, token_scopes):
	payload = json.dumps({"name": token_name, "scopes": token_scopes})
	r = dynatrace_api.post_object(f'{env}{endpoint}', token, payload)
	token_posted = r.json()
	print(f'Created token named "{token_name}" with scopes: {token_scopes}: {token_posted.get("token")}')
	print(f'Be sure to save the token displayed below in your password keeper/secrets manager/vault!')
	print(f'{token_posted.get("token")}')

	# return a full token object rather than skimpy one returned from POST
	return get_token(token_posted.get('id'))


def put_token(token_id, payload):
	dynatrace_api.put_object(f'{env}{endpoint}/{token_id}', token, payload)


def get_token(token_id):
	# If a secret is passed as the token id, shorten it
	token_split = token_id.split('.')
	shortened_token_id = f'{token_split[0]}.{token_split[1]}'
	r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{shortened_token_id}', token)
	return r.json()


def delete_token(token_id):
	dynatrace_api.delete_object(f'{env}{endpoint}/{token_id}', token)
	print(f'Deleted token with id {token_id}')


def rotate_token(token_id):
	old_token = get_token(token_id)
	old_token.pop('id')
	old_token.pop('creationDate')
	r = dynatrace_api.post_object(f'{env}{endpoint}', token, json.dumps(old_token))
	new_token = r.json()
	delete_token(token_id)
	print('Rotated tokens: ' + token_id + ' -> ' + str(new_token))
	return new_token


def list_tokens():
	token_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

	formatted_token_details = []

	for token_json in token_json_list:
		inner_token_json_list = token_json.get('apiTokens')
		for inner_token_json in inner_token_json_list:
			token_detail_id = inner_token_json.get('id')
			token_detail_name = inner_token_json.get('name')
			token_detail_enabled = inner_token_json.get('enabled')
			token_detail_owner = inner_token_json.get('owner')
			token_detail_creation_date = inner_token_json.get('creationDate')
			formatted_token_detail = token_detail_name + '|' + token_detail_owner + '|' + str(token_detail_enabled) + '|' + token_detail_creation_date + '|' + token_detail_id
			formatted_token_details.append(formatted_token_detail)

	for formatted_token_detail in sorted(formatted_token_details):
		# if formatted_token_detail[0] != '|' and 'mauney' in formatted_token_detail.lower():
		if True:
			print(formatted_token_detail)


def test():
	pass

	print('Test creating each token type, and delete each after creation')
	test_token = post_api_token()
	delete_token(test_token.get('id'))
	test_token = post_dashboard_generator_token()
	delete_token(test_token.get('id'))
	test_token = post_esa_token()
	delete_token(test_token.get('id'))
	test_token = post_logs_ingest_token()
	delete_token(test_token.get('id'))
	test_token = post_monaco_token()
	delete_token(test_token.get('id'))
	test_token = post_mute_tenable_token()
	delete_token(test_token.get('id'))
	test_token = post_problem_analysis_token()
	delete_token(test_token.get('id'))
	test_token = post_read_metrics_token()
	delete_token(test_token.get('id'))
	test_token = post_reporting_token()
	delete_token(test_token.get('id'))
	test_token = post_tools_token()
	delete_token(test_token.get('id'))
	test_token = post_tools_token_without_log_export()
	delete_token(test_token.get('id'))
	test_token = post_super_reader_token()
	delete_token(test_token.get('id'))
	test_token = post_test_token()
	delete_token(test_token.get('id'))
	test_token = post_terraform_read_token()
	delete_token(test_token.get('id'))
	print('')

	print('Test rotating a token')
	test_token = post_test_token()
	rotated_token = rotate_token(test_token.get('id'))
	delete_token(rotated_token.get('id'))
	print('')

	print('Test listing tokens')
	list_tokens()
	print('')

	print('Test getting a token')
	test_token = post_test_token()
	print('get:', get_token(test_token.get('id')))
	delete_token(test_token.get('id'))
	print('')

	print('Test update (put_token)')
	test_token = post_test_token()
	print(f'Before Update: {test_token}')
	test_token['enabled'] = False
	put_token(test_token.get('id'), json.dumps(test_token))
	updated_test_token = get_token(test_token.get('id'))
	print(f'After Update: {updated_test_token}')
	delete_token(test_token.get('id'))
	print('')


if __name__ == '__main__':
	process()
