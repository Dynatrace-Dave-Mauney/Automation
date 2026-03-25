import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

host_lookup = {}


def process(env, main_token, remote_config_token):
	pass
	# clear_some_tier_0_tags(env, main_token, remote_config_token)
	# set_some_tier_0_tags(env, main_token, remote_config_token)

	# clear_some_tier_1_tags(env, main_token, remote_config_token)
	# set_some_tier_1_tags(env, main_token, remote_config_token)

	# clear_all_tier_0_tags(env, main_token, remote_config_token)

	get_current_job(env, remote_config_token)
	# get_finished_jobs(env, remote_config_token, True)


def clear_some_tier_0_tags(env, main_token, remote_config_token):
	apps_to_clear = [
	'dsrip',
	'omnicell',
	]
	host_id_list = []
	endpoint = '/api/v2/entities'
	# raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
	raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
	params = urllib.parse.quote(raw_params, safe='/,&=?')
	entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
	for entities_json in entities_json_list:
		inner_entities_json_list = entities_json.get('entities')
		for inner_entities_json in inner_entities_json_list:
			entity_id = inner_entities_json.get('entityId', '')
			display_name = inner_entities_json.get('displayName', '')
			tags = inner_entities_json.get('tags', [])
			if "'key': 'primary_tags.tier', 'value': '0'" in str(tags):
				app_tag = get_tag(tags)
				if app_tag in apps_to_clear:
					print(f'Removing tier:0 tag for app {app_tag}:', display_name, entity_id)
					host_id_list.append(entity_id)

	post_host_tag_job(env, remote_config_token, host_id_list, 'clear', 'primary_tags.tier=0')


def set_some_tier_0_tags(env, main_token, remote_config_token):
	apps_to_set = [
		'active-directory',
		'ad-azure-password',
		'ad-utility-server',
		'adfr-dc-shared',
		'adfs',
		'azure-ad-connect',
		'domain-controller',
		'exchange',
	]
	apps_to_set = [
		'beyondtrust',
		'beyond-trust-password-safe',
		'net-backup',
		'powerpath',
		'symantec-vip',
		'ukg-kronos-time-attendance-mssn'
	]

	host_id_list = []
	endpoint = '/api/v2/entities'
	raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
	params = urllib.parse.quote(raw_params, safe='/,&=?')
	entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
	for entities_json in entities_json_list:
		inner_entities_json_list = entities_json.get('entities')
		for inner_entities_json in inner_entities_json_list:
			entity_id = inner_entities_json.get('entityId', '')
			display_name = inner_entities_json.get('displayName', '')
			tags = inner_entities_json.get('tags', [])
			app_tag = get_tag(tags)
			if app_tag in apps_to_set:
				print(f'Setting tier:0 tag for app {app_tag}:', display_name, entity_id)
				host_id_list.append(entity_id)

	post_host_tag_job(env, remote_config_token, host_id_list, 'set', 'primary_tags.tier=0')


def clear_some_tier_1_tags(env, main_token, remote_config_token):
	apps_to_clear = [
	'3m',
	'3m-enterprise-crs-application-server',
	'3m-enterprise-hdm-app-prod-server',
	'3m-enterprise-interface-prod-server',
	'3m-enterprise-rep-core-server',
	'3m-enterprise-report-prod-server',
	'3m-enterprise-sql-prod-server',
	'3m-enterprise-web-prod-server',
	'edr',
	'exchange',
	'geviewpoint',
	'qpathe',
	'symantec-vip',
	'ukg-kronos-time-attendance-mssn',
	]
	apps_to_clear = [
	'ad-azure-password',
	'adfr-dc-shared',
	'azure-ad-connect',
	'exchange',
	]
	apps_to_clear = [
		'beyondtrust',
		'beyond-trust-password-safe',
		'net-backup',
		'powerpath',
		'symantec-vip',
		'ukg-kronos-time-attendance-mssn'
	]
	host_id_list = []
	endpoint = '/api/v2/entities'
	# raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
	raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
	params = urllib.parse.quote(raw_params, safe='/,&=?')
	entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
	for entities_json in entities_json_list:
		inner_entities_json_list = entities_json.get('entities')
		for inner_entities_json in inner_entities_json_list:
			entity_id = inner_entities_json.get('entityId', '')
			display_name = inner_entities_json.get('displayName', '')
			tags = inner_entities_json.get('tags', [])
			if "'key': 'primary_tags.tier', 'value': '1'" in str(tags):
				app_tag = get_tag(tags)
				if app_tag in apps_to_clear:
					print(f'Removing tier:1 tag for app {app_tag}:', display_name, entity_id)
					host_id_list.append(entity_id)

	post_host_tag_job(env, remote_config_token, host_id_list, 'clear', 'primary_tags.tier=1')

def set_some_tier_1_tags(env, main_token, remote_config_token):
	# apps_to_set = [
	# 	'aig',
	# 	'beyond-trust-password-safe',
	# 	'ge-pacs',
	# 	'sectra',
	# 	'ukg-kronos-time-&-attendance-mssn',
	# ]
	apps_to_set = [
		'qpathe',
		'symantec-vip',
		'ukg-kronos-time-attendance-mssn',
	]

	host_id_list = []
	endpoint = '/api/v2/entities'
	# raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
	raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
	params = urllib.parse.quote(raw_params, safe='/,&=?')
	entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
	for entities_json in entities_json_list:
		inner_entities_json_list = entities_json.get('entities')
		for inner_entities_json in inner_entities_json_list:
			entity_id = inner_entities_json.get('entityId', '')
			display_name = inner_entities_json.get('displayName', '')
			tags = inner_entities_json.get('tags', [])
			app_tag = get_tag(tags)
			if app_tag in apps_to_set:
				print(f'Setting tier:1 tag for app {app_tag}:', display_name, entity_id)
				host_id_list.append(entity_id)

	post_host_tag_job(env, remote_config_token, host_id_list, 'set', 'primary_tags.tier=1')

def clear_all_tier_0_tags(env, main_token, remote_config_token):
	host_id_list = []
	endpoint = '/api/v2/entities'
	# raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
	raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
	params = urllib.parse.quote(raw_params, safe='/,&=?')
	entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
	for entities_json in entities_json_list:
		inner_entities_json_list = entities_json.get('entities')
		for inner_entities_json in inner_entities_json_list:
			entity_id = inner_entities_json.get('entityId', '')
			display_name = inner_entities_json.get('displayName', '')
			properties = inner_entities_json.get('properties')
			tags = inner_entities_json.get('tags', [])
			if "'key': 'primary_tags.tier', 'value': '0'" in str(tags):
				print('Tier0:', display_name, entity_id)
				host_id_list.append(entity_id)
			# host_lookup[display_name] = entity_id
			else:
				print('Tier1:', display_name, entity_id)

	post_host_tag_job(env, remote_config_token, host_id_list, 'clear', 'primary_tags.tier=0')


def get_tag(tags):
	app_tag = None
	for tag in tags:
		if "'key': 'primary_tags.app'" in str(tag):
			app_tag = tag.get('value')
			# print(app_tag, tag)

	return app_tag


	########################################################################################################
	#                                                                                                      #
	#                                             OBSOLETE                                                 #
	#                                                                                                      #
	########################################################################################################

	# host_list = [
	# # CUSTOMER
	# 'zeuspwcxnyh001.msnyuhealth.org',
	# # PERSONAL
	# # 'DT-8VBQQV3 accounting_app_prod',
	# ]
	#
	# host_id_list = []
	# for host in host_list:
	# 	host_id = get_host_id(host)
	# 	host_id_list.append(host_id)

	# post_host_tag_job(host_id_list, 'clear', 'primary_tags.app=nyee-user-file-shares')
	# post_host_tag_job(host_id_list, 'clear', 'primary_tags.function=db-sql')
	# get_current_job()

	# get_finished_jobs(env, remote_config_token, True)
	# post_host_tag_job(host_id_list, 'clear', 'primary_tags.zone=azure')
	# post_host_tag_job(host_id_list, 'set', 'primary_tags.zone=notazure')


# def get_host_id(host):
# 	return host_lookup[host]


########################################################################################################
#                                                                                                      #
#                                             USEFUL                                                 #
#                                                                                                      #
########################################################################################################

def post_host_tag_job(env, token, host_id_list, operation, tag):
	endpoint = '/api/v2/oneagents/remoteConfigurationManagement'
	payload_dict = {
  "entities": [],
  "operations": [
    {
      "attribute": "hostTag",
      "operation": f"{operation}",
      "value": f"{tag}"
    }
  ]
}
	payload_dict['entities'] = host_id_list
	payload = json.dumps(payload_dict)
	print(payload)
	# post_validate_payload(payload)
	# exit(9999)
	r = dynatrace_api.post_object(f'{env}{endpoint}', token, payload)
	print(r, r.status_code, r.text)


def post_validate_payload(env, token, payload):
	endpoint = '/api/v2/oneagents/remoteConfigurationManagement/validator'
	r = dynatrace_api.post_object(f'{env}{endpoint}', token, payload)
	print(r, r.status_code, r.text)


def get_current_job(env, token):
	endpoint = '/api/v2/oneagents/remoteConfigurationManagement/current'
	r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
	print(r, r.status_code, r.text)
	if r.status_code == 204:
		print('No remote configuration management job is currently running')
	else:
		json_list = r.json()
		print(json_list)
		for json in json_list:
			print(json)


def get_finished_jobs(env, token, most_recent):
	endpoint = '/api/v2/oneagents/remoteConfigurationManagement'
	r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
	print(r, r.status_code, r.text)
	json_response = r.json()
	print(json_response)
	json_list = json_response.get('jobs')
	for job in json_list:
		job_id = job.get('id')
		get_job(env, token, job_id)
		if most_recent:
			return


def get_job(env, token, job_id):
	endpoint = f'/api/v2/oneagents/remoteConfigurationManagement/{job_id}'
	r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
	print(r, r.status_code, r.text)
	json_list = r.json()
	print(json_list)


# OBSOLETE
def post_job(env, token, host_id_list):
	endpoint = '/api/v2/oneagents/remoteConfigurationManagement'
	payload_dict = {
  "entities": [],
  "operations": [
    {
      "attribute": "networkZone",
      "operation": "set",
      "value": "azure"
    }
  ]
}
	payload_dict['entities'] = host_id_list
	payload = json.dumps(payload_dict)
	r = dynatrace_api.post_object(f'{env}{endpoint}', token, payload)
	print(r, r.status_code, r.text)


if __name__ == '__main__':
	friendly_function_name = 'Dynatrace Automation Reporting'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'Personal'
	env_name, env, main_token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

	# Use a new token later, this is a hack
	configuration_file = 'configurations.yaml'
	remote_config_token = environment.get_configuration('token', configuration_file=configuration_file)

	if not env or not main_token or not remote_config_token:
		print('Env or Token Environment Variable Not Set!')
		exit(1)

	process(env, main_token, remote_config_token)
