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

object_cache = {}


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


def update(config_endpoint, tag_name, key, value):
	global object_cache
	# print('update(' + config_endpoint + ',' + tag_name + ',' + key + ',' + value + ')')
	endpoint = '/api/config/v1/' + config_endpoint

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

		print(object_cache)

	object_id = object_cache[endpoint].get(tag_name)
	config_object = json.loads(get_by_object_id(endpoint, object_id).text)

	# print(object)

	# print(key)
	current_value = config_object.get(key)

	# print('Current value of ' + key + ': ' + str(current_value))

	config_object[key] = value

	print(config_object)

	put(endpoint, object_id, json.dumps(config_object))

	print('For "' + tag_name + '" (' + endpoint + '/' + object_id + ') ' + key + ' changed from "' + str(current_value) + '" to + "' + str(value) + '"')


def process():
	# For when everything is commented out below...
	pass

	auto_tag_updates = [
		('AWS Availability Zone', 'description', 'Filter a dashboard or view to an AWS availability zone'),
		('AWS Region', 'description', 'Filter a dashboard or view to an AWS region'),
		('Amazon ECR Image Account Id', 'description', 'Filter a dashboard or view to an Amazon ECR Image Account Id'),
		('Amazon ECR Image Region', 'description', 'Filter a dashboard or view to an Amazon ECR Image Region'),
		('Amazon ECS Cluster', 'description', 'Filter a dashboard or view to an Amazon ECS Cluster'),
		('Amazon ECS Container Name', 'description', 'Filter a dashboard or view to an Amazon ECS Container Name'),
		('Amazon ECS Family', 'description', 'Filter a dashboard or view to an Amazon ECS Family'),
		('Amazon ECS Revision', 'description', 'Filter a dashboard or view to an Amazon ECS Revision'),
		('Amazon Lambda Function Name', 'description', 'Filter a dashboard or view to an Amazon Lambda Function Name'),
		('Apache Config Path', 'description', 'Filter a dashboard or view to an Apache Config Path'),
		('Asp Dot Net Core Application Path', 'description', 'Filter a dashboard or view to an Asp Dot Net Core Application Path'),
		('Catalina Base', 'description', 'Filter a dashboard or view to a Tomcat Catalina Base'),
		('Catalina Home', 'description', 'Filter a dashboard or view to a Tomcat Catalina Home'),
		('Cloud Provider', 'description', 'Filter a dashboard or view to a cloud provider'),
		('Command Line Args', 'description', 'Filter a dashboard or view to specific Command Line Args'),
		('Data Center', 'description', 'Filter a dashboard or view to a data center'),
		('Database Vendor', 'description', 'Filter a dashboard or view to a specific Database Vendor'),
		('Dot Net Command Path', 'description', 'Filter a dashboard or view to a Dot Net Command Path'),
		('Dot Net Command', 'description', 'Filter a dashboard or view to a Dot Net Command'),
		('Exe Name', 'description', 'Filter a dashboard or view to an Exe Name'),
		('Exe Path', 'description', 'Filter a dashboard or view to an Exe Path'),
		('Geolocation', 'description', 'The geographic location returned from MaxMind for the IP address of the host'),
		('Host CPU Cores', 'description', 'Filter a dashboard or view to a'),
		('Host Group', 'description', 'Filter a dashboard or view to host group.  Especially useful on views that do not have a built-in host group filter.'),
		('Host Name', 'description', 'Filter a dashboard or view to a single host'),
		# ('Host Technology', 'description', 'Filter a dashboard or view to a host technology detected by Dynatrace'),
		('IBM Integration Node Name', 'description', 'Filter a dashboard or view to an IBM Integration Node Name'),
		('IBM Integration Server Name', 'description', 'Filter a dashboard or view to an IBM Integration Server Name'),
		('IIS App Pool', 'description', 'Filter a dashboard or view to an IIS application pool'),
		('IIS Role Name', 'description', 'Filter a dashboard or view to an IIS Role Name'),
		('IP Address', 'description', 'Filter a dashboard or view to an IP address'),
		('Java Jar File', 'description', 'Filter a dashboard or view to a'),
		('Java Jar Path', 'description', 'Filter a dashboard or view to a Java Jar Path'),
		('Kubernetes Base Pod Name', 'description', 'Filter a dashboard or view to a Kubernetes Base Pod Name'),
		('Kubernetes Cluster', 'description', 'Filter a dashboard or view to a Kubernetes Cluster'),
		('Kubernetes Container Name', 'description', 'Filter a dashboard or view to a Kubernetes Container Name'),
		('Kubernetes Full Pod Name', 'description', 'Filter a dashboard or view to a Kubernetes Full Pod Name'),
		('Kubernetes Namespace', 'description', 'Filter a dashboard or view to a Kubernetes Namespace'),
		('Kubernetes Pod UID', 'description', 'Filter a dashboard or view to a Kubernetes Pod UID'),
		('Node JS Script Name', 'description', 'Filter a dashboard or view to a NodeJS App Base Director'),
		('NodeJS App Base Director', 'description', 'Filter a dashboard or view to a'),
		('NodeJS App Name', 'description', 'Filter a dashboard or view to a Java Jar File'),
		('OS', 'description', 'Filter a dashboard or view to a specific operating system'),
		('Oracle SID', 'description', 'Filter a dashboard or view to the specific number of Host CPU Cores'),
		('Process Group Name', 'description', 'Filter a dashboard or view to a single process group'),
		('Service Name', 'description', 'Filter a dashboard or view to a single service'),
		('Service Topology Type', 'description', 'Filter a dashboard or view to a Service Topology Type (Fully Monitored, External or Opaque).'),
		('SpringBootAppName', 'description', 'Filter a dashboard or view to a SpringBoot Application Name'),
		('SpringBootProfileName', 'description', 'Filter a dashboard or view to a SpringBoot Profile Name'),
		('SpringBootStartupClass', 'description', 'Filter a dashboard or view to a SpringBoot Startup Class'),
		('Technology', 'description', 'Filter a dashboard or view to specific technology detected by Dynatrace'),
		('VMWare Data Center Name', 'description', 'Filter a dashboard or view to a VMWare Data Center Name'),
		('VMWare VM Name', 'description', 'Filter a dashboard or view to a VMWare Virtual Machine Name'),
		('Web Application ID', 'description', 'Filter a dashboard or view to a Web Application ID'),
		('Web Application Name', 'description', 'Filter a dashboard or view to a single web application'),
		('Web Context Root', 'description', 'Filter a dashboard or view to a Web Context Root'),
		('Web Server Name', 'description', 'Filter a dashboard or view to a Web Server Name'),
		('Web Service Name', 'description', 'Filter a dashboard or view to a Web Service Name'),
		('Web Service Namespace', 'description', 'Filter a dashboard or view to a Web Service Namespace'),
		('WebLogic Cluster', 'description', 'Filter a dashboard or view to a WebLogic Cluster'),
		('WebLogic Domain', 'description', 'Filter a dashboard or view to a WebLogic Domain'),
		('WebLogic Home', 'description', 'Filter a dashboard or view to a WebLogic Home'),
		('WebLogic Name', 'description', 'Filter a dashboard or view to a WebLogic Name'),
		('WebSphere Cell', 'description', 'Filter a dashboard or view to a WebSphere Cell'),
		('WebSphere Cluster', 'description', 'Filter a dashboard or view to a WebSphere Cluster'),
		('WebSphere Node', 'description', 'Filter a dashboard or view to a WebSphere Node'),
		('WebSphere Server', 'description', 'Filter a dashboard or view to a WebSphere Server')
	]

	for auto_tag_update in auto_tag_updates:
		name = auto_tag_update[0]
		key = auto_tag_update[1]
		value = auto_tag_update[2]
		if value != '':
			print(name + ': ' + key + ': ' + value)
			update('autoTags', name, key, value)

	# update('autoTags', '  Host Name', 'description', 'Filter a dashboard or view to a single host.')


if __name__ == '__main__':
	process()
