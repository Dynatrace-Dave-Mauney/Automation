import copy
from inspect import currentframe
import json
import os
import requests
import ssl

# env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

tenant = os.environ.get(tenant_key)
token = os.environ.get(token_key)
env = f'https://{tenant}.live.dynatrace.com'

management_zone_updates = [
	'NONE',
]

object_cache = {}


def post(endpoint, payload):
	json_data = json.loads(payload)
	formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)
	url = env + endpoint
	# print('POST: ' + url)
	# print('payload: ' + formatted_payload)
	try:
		r = requests.post(url, payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
		print('Status Code: %d' % r.status_code)
		print('Reason: %s' % r.reason)
		if len(r.text) > 0:
			print(r.text)
		if r.status_code not in [200, 201, 204]:
			# print(json_data)
			error_filename = '$post_error_payload.json'
			with open(error_filename, 'w') as file:
				file.write(formatted_payload)
				name = json_data.get('name')
				if name:
					print('Name: ' + name)
				print('Error in "post(env, endpoint, token, payload)" method')
				print('Exit code shown below is the source code line number of the exit statement invoked')
				print('See ' + error_filename + ' for more details')
			exit(get_linenumber())
		return r
	except ssl.SSLError:
		print('SSL Error')
		exit(get_linenumber())


def put(endpoint, object_id, payload):
	json_data = json.dumps(json.loads(payload), indent=4, sort_keys=False)
	url = env + endpoint + '/' + object_id
	# print('PUT: ' + url)
	# print('payload: ' + json_data)
	try:
		r = requests.put(url, json_data.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
		print('Status Code: %d' % r.status_code)
		print('Reason: %s' % r.reason)
		if len(r.text) > 0:
			print(r.text)
		if r.status_code not in [200, 201, 204]:
			# print(json_data)
			error_filename = '$put_error_payload.json'
			with open(error_filename, 'w') as file:
				file.write(json_data)
				print('Error in "put(env, endpoint, token, object_id, payload)" method')
				print('Exit code shown below is the source code line number of the exit statement invoked')
				print('See ' + error_filename + ' for more details')
			exit(get_linenumber())
		return r
	except ssl.SSLError:
		print('SSL Error')
		exit(get_linenumber())


def get_by_object_id(endpoint, object_id):
	url = env + endpoint + '/' + object_id
	# print('GET: ' + url)
	try:
		r = requests.get(url, params='', headers={'Authorization': 'Api-Token ' + token})
		if r.status_code not in [200]:
			print('Error in "get_by_object_id(endpoint, object_id)" method')
			print('Endpoint: ' + endpoint)
			print('Object ID: ' + object_id)
			print('Exit code shown below is the source code line number of the exit statement invoked')
			exit(get_linenumber())
		return r
	except ssl.SSLError:
		print('SSL Error')
		exit(get_linenumber())


def get_object_list(endpoint):
	url = env + endpoint
	# print('GET: ' + url)
	try:
		r = requests.get(url, params='', headers={'Authorization': 'Api-Token ' + token})
		if r.status_code not in [200]:
			print('Error in "get_object_list(endpoint)" method')
			print('Endpoint: ' + endpoint)
			print('Exit code shown below is the source code line number of the exit statement invoked')
			exit(get_linenumber())
		return r
	except ssl.SSLError:
		print('SSL Error')
		exit(get_linenumber())


def get_linenumber():
	cf = currentframe()
	return cf.f_back.f_lineno


def update(management_zone_name):
	global object_cache
	endpoint = '/api/config/v1/managementZones'
	tag = 'Host Group:' + management_zone_name
	
	if not object_cache.get(endpoint):
		r = get_object_list(endpoint)

		# print(r.text)

		config_json = json.loads(r.text)
		config_list = config_json.get('values')
		config_dict = {}
		for config in config_list:
			object_id = copy.deepcopy(config.get('id'))
			name = copy.deepcopy(config.get('name'))
			config_dict[name] = object_id

		object_cache[endpoint] = config_dict

		# print(object_cache)

	additional_dimensional_rules = [
		{
			"appliesTo": "METRIC",
			"conditions": [
				{
					"conditionType": "METRIC_KEY",
					"key": "ext:tech.SAP_HANADB",
					"ruleMatcher": "BEGINS_WITH",
					"value": None
				}
			],
			"enabled": True
		},
		{
			"appliesTo": "METRIC",
			"conditions": [
				{
					"conditionType": "METRIC_KEY",
					"key": "ext:tech.datapower",
					"ruleMatcher": "BEGINS_WITH",
					"value": None
				}
			],
			"enabled": True
		}
	]

	additional_entity_selector_based_rules = [
		{
			"enabled": True,
			"entitySelector": "type(HOST),toRelationships.runsOnHost(type(SERVICE),toRelationships.calls(type(SERVICE),tag({{.tag}})))"
		},
		{
			"enabled": True,
			"entitySelector": "type(HOST),toRelationships.runsOnHost(type(SERVICE),fromRelationships.calls(type(SERVICE),tag({{.tag}})))"
		},
		{
			"enabled": True,
			"entitySelector": "type(SERVICE),toRelationships.calls(type(SERVICE),tag({{.tag}}))"
		},
		{
			"enabled": True,
			"entitySelector": "type(SERVICE),fromRelationships.calls(type(SERVICE),tag({{.tag}}))"
		},
		{
			"enabled": True,
			"entitySelector": "type(PROCESS_GROUP),toRelationships.runsOn(type(SERVICE),fromRelationships.calls(type(SERVICE),tag({{.tag}})))"
		},
		{
			"enabled": True,
			"entitySelector": "type(PROCESS_GROUP),toRelationships.runsOn(type(SERVICE),toRelationships.calls(type(SERVICE),tag({{.tag}})))"
		}
	]

	object_id = object_cache[endpoint].get(management_zone_name)
	config_object = json.loads(get_by_object_id(endpoint, object_id).text)

	# print(config_object)

	# print(key)

	# print('Current value of ' + key + ': ' + str(current_value))

	# dimensional_rules = object.get('dimensionalRules')
	# entity_selector_based_rules = object.get('entitySelectorBasedRules')

	# Does not rename variable "tag"
	# dimensional_rules.extend(additional_dimensional_rules)
	# entity_selector_based_rules.extend( additional_entity_selector_based_rules)

	new_entity_selector_based_rules = []
	for additional_entity_selector_based_rule in additional_entity_selector_based_rules:
		entity_selector = additional_entity_selector_based_rule.get('entitySelector')
		# print(entitySelector)
		new_entity_selector = entity_selector.replace('{{.tag}}', tag)
		# print(new_entity_selector)
		additional_entity_selector_based_rule['entitySelector'] = new_entity_selector
		new_entity_selector_based_rules.append(additional_entity_selector_based_rule)

	config_object['name'] = management_zone_name + ' (Full Flow)'
	config_object['dimensionalRules'].extend(additional_dimensional_rules)
	config_object['entitySelectorBasedRules'].extend(new_entity_selector_based_rules)
	config_object.pop('id')

	# print(dimensional_rules)
	# print(entity_selector_based_rules)

	# print(config_object)

	# put(endpoint, object_id, json.dumps(config_object))
	post(endpoint, json.dumps(config_object))


def process():
	# For when everything is commented out below...
	pass

	for management_zone_update in management_zone_updates:
		update(management_zone_update)


if __name__ == '__main__':
	process()
