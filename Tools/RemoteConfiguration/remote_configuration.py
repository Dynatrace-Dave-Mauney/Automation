import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

friendly_function_name = 'Dynatrace Automation Reporting'
env_name_supplied = environment.get_env_name(friendly_function_name)
env_name_supplied = 'Prod'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

# Use a new token later, this is a hack
configuration_file = 'configurations.yaml'
token2 = token
token = environment.get_configuration('token', configuration_file=configuration_file)

print('Token:', token)

host_lookup = {}
endpoint = '/api/v2/entities'
raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m'
params = urllib.parse.quote(raw_params, safe='/,&=?')
entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token2, params=params)
for entities_json in entities_json_list:
	inner_entities_json_list = entities_json.get('entities')
	for inner_entities_json in inner_entities_json_list:
		entity_id = inner_entities_json.get('entityId', '')
		display_name = inner_entities_json.get('displayName', '')
		host_lookup[display_name] = entity_id


def process():
	if not env or not token:
		print('Env or Token Environment Variable Not Set!')
		exit(1)

	host_list = [
		# 'SEBAAPPP019004.msnyuhealth.org',
		# 'SEBAAPPP019005.msnyuhealth.org',
		# 'SEBAAPPP019006.msnyuhealth.org',
		# 'SEBAAPPP019007.msnyuhealth.org',
		# 'sEBAAppP019001.msnyuhealth.org',
		# 'sEBAAppP019002.msnyuhealth.org',
		# 'sEBAAppP019003.msnyuhealth.org',
	]

	host_id_list = []
	for host in host_list:
		host_id = get_host_id(host)
		host_id_list.append(host_id)


	post_job_preview(host_id_list)
	# post_job(host_id_list)


def get_host_id(host):
	return host_lookup[host]

def post_job_preview(host_id_list):
	endpoint = '/api/v2/oneagents/remoteConfigurationManagement/preview'
	payload_dict = {
  "entities": [],
  "operations": [
    {
      "attribute": "networkZone",
      "operation": "set",
      "value": "onprem"
    }
  ]
}
	payload_dict['entities'] = host_id_list
	payload = json.dumps(payload_dict)
	r = dynatrace_api.post_object(f'{env}{endpoint}', token, payload)
	print(r, r.status_code, r.text)


def post_job(host_id_list):
	endpoint = '/api/v2/oneagents/remoteConfigurationManagement'
	payload_dict = {
  "entities": [],
  "operations": [
    {
      "attribute": "networkZone",
      "operation": "set",
      "value": "onprem"
    }
  ]
}
	payload_dict['entities'] = host_id_list
	payload = json.dumps(payload_dict)
	r = dynatrace_api.post_object(f'{env}{endpoint}', token, payload)
	print(r, r.status_code, r.text)


if __name__ == '__main__':
	process()
