import copy
import json

from Reuse import dynatrace_api
from Reuse import environment

# env_name, env, token = environment.get_environment('Prod')
# env_name, env, token = envi	ronment.get_environment('NonProd')
# env_name, env, token = environment.get_environment('Prep')
# env_name, env, token = environment.get_environment('Dev')
env_name, env, token = environment.get_environment('Personal')
# env_name, env, token = environment.get_environment('Demo')

print('Update Tag Descriptions')

object_cache = {}


def update(config_endpoint, tag_name, key, value):
	# print(f'update({config_endpoint}, {tag_name}, {key}, {value})')
	global object_cache
	# print('update(' + config_endpoint + ',' + tag_name + ',' + key + ',' + value + ')')
	endpoint = '/api/config/v1/' + config_endpoint

	if not object_cache.get(endpoint):
		r = dynatrace_api.get_object_list(env, token, endpoint)

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

	object_id = object_cache[endpoint].get(tag_name)

	# If the object does not exist on the tenant there is nothing to do
	if not object_id:
		return

	# print(f'object_id: {object_id}')

	config_object = dynatrace_api.get_by_object_id(env, token, endpoint, object_id)

	# print(object)

	# print(key)
	current_value = config_object.get(key)

	# print('Current value of ' + key + ': ' + str(current_value))

	config_object[key] = value

	# print(config_object)

	dynatrace_api.put(env, token, endpoint, object_id, json.dumps(config_object))

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
		('Apache Spark Master Ip Address', 'description', 'Filter a dashboard or view to a Apache Spark Master Ip Address'),
		('Asp Dot Net Core Application Path', 'description', 'Filter a dashboard or view to an Asp Dot Net Core Application Path'),
		('Cassandra Cluster Name', 'description', 'Filter a dashboard or view to a Cassandra Cluster Name'),
		('Catalina Base', 'description', 'Filter a dashboard or view to a Tomcat Catalina Base'),
		('Catalina Home', 'description', 'Filter a dashboard or view to a Tomcat Catalina Home'),
		('Cloud Foundry App Id', 'description', 'Filter a dashboard or view to a Cloud Foundry App Id'),
		('Cloud Foundry App Name', 'description', 'Filter a dashboard or view to a Cloud Foundry App Name'),
		('Cloud Foundry Instance Index', 'description', 'Filter a dashboard or view to a Cloud Foundry Instance Index'),
		('Cloud Foundry Space Id', 'description', 'Filter a dashboard or view to a Cloud Foundry Space Id'),
		('Cloud Foundry Space Name', 'description', 'Filter a dashboard or view to a Cloud Foundry Space Name'),
		('Cloud Provider', 'description', 'Filter a dashboard or view to a cloud provider'),
		('Cold Fusion Jvm Config File', 'description', 'Filter a dashboard or view to a Cold Fusion Jvm Config File'),
		('Cold Fusion Service Name', 'description', 'Filter a dashboard or view to a Cold Fusion Service Name'),
		('Command Line Args', 'description', 'Filter a dashboard or view to specific Command Line Args'),
		('Data Center', 'description', 'Filter a dashboard or view to a data center'),
		('Database Vendor', 'description', 'Filter a dashboard or view to a specific Database Vendor'),
		('Dot Net Command Path', 'description', 'Filter a dashboard or view to a Dot Net Command Path'),
		('Dot Net Command', 'description', 'Filter a dashboard or view to a Dot Net Command'),
		('Elasticsearch Cluster Name', 'description', 'Filter a dashboard or view to a Elasticsearch Cluster Name'),
		('Elasticsearch Node Name', 'description', 'Filter a dashboard or view to a Elasticsearch Node Name'),
		('Equinox Config Path', 'description', 'Filter a dashboard or view to a Equinox Config Path'),
		('Exe Name', 'description', 'Filter a dashboard or view to an Exe Name'),
		('Exe Path', 'description', 'Filter a dashboard or view to an Exe Path'),
		('Geolocation', 'description', 'The geographic location returned from MaxMind for the IP address of the host'),
		('GlassFish Domain Name', 'description', 'Filter a dashboard or view to a GlassFish Domain Name'),
		('GlassFish Instance Name', 'description', 'Filter a dashboard or view to a GlassFish Instance Name'),
		('Google App Engine Instance', 'description', 'Filter a dashboard or view to a Google App Engine Instance'),
		('Google App Engine Service', 'description', 'Filter a dashboard or view to a Google App Engine Service'),
		('Google Cloud Project', 'description', 'Filter a dashboard or view to a Google Cloud Project'),
		('Host CPU Cores', 'description', 'Filter a dashboard or view to hosts with a given number of CPU cores'),
		('Host Group', 'description', 'Filter a dashboard or view to host group.  Especially useful on views that do not have a built-in host group filter.'),
		('Host Name', 'description', 'Filter a dashboard or view to a single host name'),
		('Host Technology', 'description', 'Filter a dashboard or view to a Host Technology'),
		('Hybris Bin Directory', 'description', 'Filter a dashboard or view to a Hybris Bin Directory'),
		('Hybris Config Directory', 'description', 'Filter a dashboard or view to a Hybris Config Directory'),
		('Hybris Data Directory', 'description', 'Filter a dashboard or view to a Hybris Data Directory'),
		('IBM CICS Region', 'description', 'Filter a dashboard or view to a IBM CICS Region'),
		# This tag is now broken, so updates fail
		# ('IBM CTG Name', 'description', 'Filter a dashboard or view to an IBM CTG Name'),
		('IBM IMS Connect Region', 'description', 'Filter a dashboard or view to a IBM IMS Connect Region'),
		('IBM IMS Control Region', 'description', 'Filter a dashboard or view to a IBM IMS Control Region'),
		('IBM IMS Message Processing Region', 'description', 'Filter a dashboard or view to a IBM IMS Message Processing Region'),
		('IBM IMS Soap GW Name', 'description', 'Filter a dashboard or view to a IBM IMS Soap GW Name'),
		('IBM Integration Node Name', 'description', 'Filter a dashboard or view to an IBM Integration Node Name'),
		('IBM Integration Server Name', 'description', 'Filter a dashboard or view to an IBM Integration Server Name'),
		('IIS App Pool', 'description', 'Filter a dashboard or view to an IIS application pool'),
		('IIS Role Name', 'description', 'Filter a dashboard or view to an IIS Role Name'),
		('IP Address', 'description', 'Filter a dashboard or view to an IP address'),
		('Java Jar File', 'description', 'Filter a dashboard or view to a Java Jar File'),
		('Java Jar Path', 'description', 'Filter a dashboard or view to a Java Jar Path'),
		('Kubernetes Base Pod Name', 'description', 'Filter a dashboard or view to a Kubernetes Base Pod Name'),
		('Kubernetes Cluster', 'description', 'Filter a dashboard or view to a Kubernetes Cluster'),
		('Kubernetes Container Name', 'description', 'Filter a dashboard or view to a Kubernetes Container Name'),
		('Kubernetes Full Pod Name', 'description', 'Filter a dashboard or view to a Kubernetes Full Pod Name'),
		('Kubernetes Namespace', 'description', 'Filter a dashboard or view to a Kubernetes Namespace'),
		('Kubernetes Pod UID', 'description', 'Filter a dashboard or view to a Kubernetes Pod UID'),
		('MS SQL Instance Name', 'description', 'Filter a dashboard or view to a MS SQL Instance Name'),
		('Node JS Script Name', 'description', 'Filter a dashboard or view to a NodeJS Script Name'),
		('NodeJS App Base Director', 'description', 'Filter a dashboard or view to a NodeJS App Base Director'),
		('NodeJS App Name', 'description', 'Filter a dashboard or view to a NodeJS App Name'),
		('OS', 'description', 'Filter a dashboard or view to a specific operating system'),
		('Oracle SID', 'description', 'Filter a dashboard or view to an Oracle SID'),
		('PHP Script Path', 'description', 'Filter a dashboard or view to a PHP Script Path'),
		('PHP Working Directory', 'description', 'Filter a dashboard or view to a PHP Working Directory'),
		('Process Group Name', 'description', 'Filter a dashboard or view to a single process group name'),
		('Ruby App Root Path', 'description', 'Filter a dashboard or view to a Ruby App Root Path'),
		('Ruby Script Path', 'description', 'Filter a dashboard or view to a Ruby Script Path'),
		('Service Name', 'description', 'Filter a dashboard or view to a single service name'),
		('Service Topology Type', 'description', 'Filter a dashboard or view to a Service Topology Type (Fully Monitored, External or Opaque).'),
		('Software AG Install Root', 'description', 'Filter a dashboard or view to a Software AG Install Root'),
		('Software AG Product Property Name', 'description', 'Filter a dashboard or view to a Software AG Product Property Name'),
		('SpringBootAppName', 'description', 'Filter a dashboard or view to a SpringBoot Application Name'),
		('SpringBootProfileName', 'description', 'Filter a dashboard or view to a SpringBoot Profile Name'),
		('SpringBootStartupClass', 'description', 'Filter a dashboard or view to a SpringBoot Startup Class'),
		('TIBCO BW App Node Name', 'description', 'Filter a dashboard or view to a TIBCO BW App Node Name'),
		('TIBCO BW App Space Name', 'description', 'Filter a dashboard or view to a TIBCO BW App Space Name'),
		('TIBCO BW CE App Name', 'description', 'Filter a dashboard or view to a TIBCO BW CE App Name'),
		('TIBCO BW CE Version', 'description', 'Filter a dashboard or view to a TIBCO BW CE Version'),
		('TIBCO BW Domain Name', 'description', 'Filter a dashboard or view to a TIBCO BW Domain Name'),
		('TIBCO BW Engine Property File Path', 'description', 'Filter a dashboard or view to a TIBCO BW Engine Property File Path'),
		('TIBCO BW Property File', 'description', 'Filter a dashboard or view to a TIBCO BW Property File'),
		('TIBCO Business Works Home', 'description', 'Filter a dashboard or view to a TIBCO Business Works Home'),
		('Technology', 'description', 'Filter a dashboard or view to specific technology detected by Dynatrace'),
		('VMWare Data Center Name', 'description', 'Filter a dashboard or view to a VMWare Data Center Name'),
		('VMWare VM Name', 'description', 'Filter a dashboard or view to a VMWare Virtual Machine Name'),
		('Varnish Instance Name', 'description', 'Filter a dashboard or view to a Varnish Instance Name'),
		('Web Application ID', 'description', 'Filter a dashboard or view to a Web Application ID'),
		('Web Application Name', 'description', 'Filter a dashboard or view to a single web application name'),
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
		('WebSphere Server', 'description', 'Filter a dashboard or view to a WebSphere Server'),
	]

	auto_tag_updates_customer_specific_no_prefix_no_suffix = [
		('AWS ALB', 'description', 'Friendly names for AWS ALB entities'),
		('AWS Availability Zone-Original', 'description', 'DEPRECATED: Use AWS Availability Zone'),
		('AWS RDS', 'description', 'Friendly names for AWS RDS entities'),
		('Apache', 'description', 'DEPRECATED: Replaced with Technology:APACHE_HTTP_SERVER'),
		('Apache_Process', 'description', 'DEPRECATED: Replaced with Technology:APACHE_HTTP_SERVER'),
		('App', 'description', 'Filter a dashboard or view to an application that is not covered fully by the standard "Application" tag'),
		('Application', 'description', 'Filter a dashboard or view to an application (which is part of the Host Group name)'),
		('Audit Tag', 'description', 'Used to enforce the Host Group naming standard'),
		('ChannelPublishingJmsMessageListener', 'description', 'DEPRECATED: Use Service Name:ChannelPublishingJmsMessageListener'),
		('Cloud Provider', 'description', 'Filter by Cloud Provider'),
		('Company', 'description', 'Filter a dashboard or view to a company (which is part of the Host Group name)'),
		('Context', 'description', 'DEPRECATED: Use Web Context Root and Technology:ORACLE_WEBLOGIC instead'),
		('Docker Worker', 'description', 'DEPRECATED: tag appears to no longer work'),
		('Environment', 'description', 'Filter a dashboard or view to an environment (which is part of the Host Group name)'),
		('IIB Server Name', 'description', 'DEPRECATED: Use IBM Integration Server Name'),
		('IIB Service', 'description', 'DEPRECATED: tag appears to no longer work'),
		('IIB', 'description', 'DEPRECATED: Use IBM Integration Server Name:All'),
		('J4LS_Cluster', 'description', 'DEPRECATED: Use WebSphere Cluster Name:J4LS'),
		('k8s Namespace', 'description', 'DEPRECATED: Use Kubernetes Namespace'),
		('Kubernetes_Namespace', 'description', 'DEPRECATED: Use Kubernetes Namespace'),
		('LLAWP', 'description', 'DEPRECATED: tag appears to no longer work'),
		('Linux', 'description', 'DEPRECATED: Use OS:Linux'),
		('Location', 'description', 'DEPRECATED: Use Data Center'),
		('MQ-QueueManager', 'description', 'Filter IBM MQ Custom Devices by the MQ Queue Manager name'),
		('OCP', 'description', 'Filter to OCP services and process groups running Apache HTTPD Siteminder'),
		('OCP_Node_Role', 'description', 'Filter hosts and process groups by OCP node role'),
		('OpenShift', 'description', 'DEPRECATED: Use Technology:OPENSHIFT'),
		('OpenShift-Origina;', 'description', 'DEPRECATED: Use Technology:OPENSHIFT'),
		('OS-Original', 'description', 'DEPRECATED: Use OS'),
		('Other Services', 'description', ''),
		('Phoenix', 'description', 'Filter process groups running Java for Phoenix'),
		('Phoenix_Global_CustomService', 'description', 'DEPRECATED: tag appears to no longer work'),
		('Phoenix_Global_MsgService', 'description', 'DEPRECATED: tag appears to no longer work'),
		('Phoenix_Informatica_Outbound', 'description', 'DEPRECATED: tag appears to no longer work'),
		('Phoenix_Java_Service', 'description', 'Filter services and process groups running Java for Phoenix'),
		('Technology-Original', 'description', 'DEPRECATED: Use Technology'),
		('Tivoli_agent', 'description', 'DEPRECATED: Use Exe Name:klzagent'),
		('Tivoli_Agent', 'description', 'DEPRECATED: Use Exe Name:klzagent'),
		('UCD', 'description', 'Filter services running ActiveMQ and referencing "air-*" java jar path'),
		('UCD_Agent', 'description', 'Filter process groups referencing "airworker.jar" or "air-monitor.jar" from the java jar path'),
		('WebSphere Cell Name', 'description', 'DEPRECATED: Use WebSphere Cell'),
		('WebSphere Cluster Name', 'description', 'DEPRECATED: Use WebSphere Cluster'),
		('WebSphere_Process', 'description', 'DEPRECATED: Use WebSphere Cluster'),
		('Websphere', 'description', 'DEPRECATED: Use WebSphere Cluster'),
		('Websphere_Cluster', 'description', 'DEPRECATED: Use WebSphere Cluster'),
		('Windows', 'description', 'DEPRECATED: Use OS:Windows'),
	]

	if env_name in ['Prod', 'Prep', 'Dev']:
		name_prefix = ''
		description_suffix = '(generated with RobotAdmin)'
		update_auto_tag_list(name_prefix, description_suffix, auto_tag_updates)
		update_auto_tag_list(None, None, auto_tag_updates_customer_specific_no_prefix_no_suffix)
	else:
		update_auto_tag_list(None, None, auto_tag_updates)


def update_auto_tag_list(name_prefix, description_suffix, auto_tag_update_list):
	for auto_tag_update in auto_tag_update_list:
		name = auto_tag_update[0]

		if name_prefix:
			name = f'{name_prefix} {name}'

		key = auto_tag_update[1]
		value = auto_tag_update[2]
		if value != '':
			if description_suffix:
				value = f'{value} {description_suffix}'

			# print(name + ': ' + key + ': ' + value)
			update('autoTags', name, key, value)


if __name__ == '__main__':
	process()
