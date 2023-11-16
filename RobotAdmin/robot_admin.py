# TODO:
# Consolidate "put_conditional_naming_rules*" methods
# Convert MZs to use fixed IDs and PUT

import copy
from inspect import currentframe
import json
import time
from requests import Response

from Reuse import dynatrace_api
from Reuse import environment

friendly_function_name = 'Dynatrace Automation'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Prod'
# env_name_supplied = 'NonProd'
# env_name_supplied = 'Prep'
# env_name_supplied = 'Dev'
# env_name_supplied = 'Personal'
# env_name_supplied = 'Demo'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

offline = False
confirmation_required = True
auto_tag_prefix = ''

fixed_auto_tag_ids = {
    'Amazon ECR Image Account Id': 'aaaaaaaa-bbbb-cccc-dddd-000000000001',
    'Amazon ECR Image Region': 'aaaaaaaa-bbbb-cccc-dddd-000000000002',
    'Amazon ECS Cluster': 'aaaaaaaa-bbbb-cccc-dddd-000000000003',
    'Amazon ECS Container Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000004',
    'Amazon ECS Family': 'aaaaaaaa-bbbb-cccc-dddd-000000000005',
    'Amazon ECS Revision': 'aaaaaaaa-bbbb-cccc-dddd-000000000006',
    'Amazon Lambda Function Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000007',
    'Amazon Region': 'aaaaaaaa-bbbb-cccc-dddd-000000000008',
    'Apache Config Path': 'aaaaaaaa-bbbb-cccc-dddd-000000000009',
    'Apache Spark Master Ip Address': 'aaaaaaaa-bbbb-cccc-dddd-000000000010',
    'Asp Dot Net Core Application Path': 'aaaaaaaa-bbbb-cccc-dddd-000000000011',
    'AWS Availability Zone': 'aaaaaaaa-bbbb-cccc-dddd-000000000012',
    'AWS Region': 'aaaaaaaa-bbbb-cccc-dddd-000000000013',
    'Azure Region': 'aaaaaaaa-bbbb-cccc-dddd-000000000116',
    'Azure Scale Set': 'aaaaaaaa-bbbb-cccc-dddd-000000000117',
    'Azure Site Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000118',
    'Cassandra Cluster Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000014',
    'Catalina Base': 'aaaaaaaa-bbbb-cccc-dddd-000000000015',
    'Catalina Home': 'aaaaaaaa-bbbb-cccc-dddd-000000000016',
    'Cloud Foundry App Id': 'aaaaaaaa-bbbb-cccc-dddd-000000000017',
    'Cloud Foundry App Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000018',
    'Cloud Foundry Instance Index': 'aaaaaaaa-bbbb-cccc-dddd-000000000019',
    'Cloud Foundry Space Id': 'aaaaaaaa-bbbb-cccc-dddd-000000000020',
    'Cloud Foundry Space Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000021',
    'Cloud Provider': 'aaaaaaaa-bbbb-cccc-dddd-000000000022',
    'Cold Fusion Jvm Config File': 'aaaaaaaa-bbbb-cccc-dddd-000000000023',
    'Cold Fusion Service Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000024',
    'Command Line Args': 'aaaaaaaa-bbbb-cccc-dddd-000000000025',
    'Data Center': 'aaaaaaaa-bbbb-cccc-dddd-000000000026',
    'Database Vendor': 'aaaaaaaa-bbbb-cccc-dddd-000000000027',
    'Dot Net Command': 'aaaaaaaa-bbbb-cccc-dddd-000000000028',
    'Dot Net Command Path': 'aaaaaaaa-bbbb-cccc-dddd-000000000029',
    'Elasticsearch Cluster Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000030',
    'Elasticsearch Node Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000031',
    'Equinox Config Path': 'aaaaaaaa-bbbb-cccc-dddd-000000000032',
    'Exe Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000033',
    'Exe Path': 'aaaaaaaa-bbbb-cccc-dddd-000000000034',
    'Geolocation': 'aaaaaaaa-bbbb-cccc-dddd-000000000035',
    'GlassFish Domain Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000036',
    'GlassFish Instance Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000037',
    'Google App Engine Instance': 'aaaaaaaa-bbbb-cccc-dddd-000000000038',
    'Google App Engine Service': 'aaaaaaaa-bbbb-cccc-dddd-000000000039',
    'Google Cloud Project': 'aaaaaaaa-bbbb-cccc-dddd-000000000040',
    'Host CPU Cores': 'aaaaaaaa-bbbb-cccc-dddd-000000000041',
    'Host Group': 'aaaaaaaa-bbbb-cccc-dddd-000000000042',
    'Host Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000043',
    'Host Technology': 'aaaaaaaa-bbbb-cccc-dddd-000000000044',
    'Hybris Bin Directory': 'aaaaaaaa-bbbb-cccc-dddd-000000000045',
    'Hybris Config Directory': 'aaaaaaaa-bbbb-cccc-dddd-000000000046',
    'Hybris Data Directory': 'aaaaaaaa-bbbb-cccc-dddd-000000000047',
    'IBM CICS Region': 'aaaaaaaa-bbbb-cccc-dddd-000000000048',
    # This one is now broken so skip it.
    # 'IBM CTG Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000049',
    'IBM IMS Connect Region': 'aaaaaaaa-bbbb-cccc-dddd-000000000050',
    'IBM IMS Control Region': 'aaaaaaaa-bbbb-cccc-dddd-000000000051',
    'IBM IMS Message Processing Region': 'aaaaaaaa-bbbb-cccc-dddd-000000000052',
    'IBM IMS Soap GW Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000053',
    'IBM Integration Node Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000054',
    'IBM Integration Server Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000055',
    'IIS App Pool': 'aaaaaaaa-bbbb-cccc-dddd-000000000056',
    'IIS Role Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000057',
    'IP Address': 'aaaaaaaa-bbbb-cccc-dddd-000000000058',
    'Java Jar File': 'aaaaaaaa-bbbb-cccc-dddd-000000000059',
    'Java Jar Path': 'aaaaaaaa-bbbb-cccc-dddd-000000000060',
    'Java Main CLass': 'aaaaaaaa-bbbb-cccc-dddd-000000000061',
    'Jboss Home': 'aaaaaaaa-bbbb-cccc-dddd-000000000062',
    'Jboss Mode': 'aaaaaaaa-bbbb-cccc-dddd-000000000063',
    'Jboss Server Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000064',
    'Kubernetes Base Pod Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000065',
    'Kubernetes Cluster': 'aaaaaaaa-bbbb-cccc-dddd-000000000066',
    'Kubernetes Container': 'aaaaaaaa-bbbb-cccc-dddd-000000000067',
    'Kubernetes Container Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000068',
    'Kubernetes Full Pod Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000069',
    'Kubernetes Namespace': 'aaaaaaaa-bbbb-cccc-dddd-000000000070',
    'Kubernetes Pod UID': 'aaaaaaaa-bbbb-cccc-dddd-000000000071',
    'MS SQL Instance Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000072',
    'Node JS Script Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000073',
    'NodeJS App Base Director': 'aaaaaaaa-bbbb-cccc-dddd-000000000074',
    'NodeJS App Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000075',
    'Oracle SID': 'aaaaaaaa-bbbb-cccc-dddd-000000000076',
    'OS': 'aaaaaaaa-bbbb-cccc-dddd-000000000077',
    'PHP Script Path': 'aaaaaaaa-bbbb-cccc-dddd-000000000078',
    'PHP Working Directory': 'aaaaaaaa-bbbb-cccc-dddd-000000000079',
    'Process Group Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000080',
    'Ruby App Root Path': 'aaaaaaaa-bbbb-cccc-dddd-000000000081',
    'Ruby Script Path': 'aaaaaaaa-bbbb-cccc-dddd-000000000082',
    'Service Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000083',
    'Service Topology Type': 'aaaaaaaa-bbbb-cccc-dddd-000000000084',
    'Software AG Install Root': 'aaaaaaaa-bbbb-cccc-dddd-000000000085',
    'Software AG Product Property Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000086',
    'SpringBootAppName': 'aaaaaaaa-bbbb-cccc-dddd-000000000087',
    'SpringBootProfileName': 'aaaaaaaa-bbbb-cccc-dddd-000000000088',
    'SpringBootStartupClass': 'aaaaaaaa-bbbb-cccc-dddd-000000000089',
    'Technology': 'aaaaaaaa-bbbb-cccc-dddd-000000000090',
    'TIBCO Business Works Home': 'aaaaaaaa-bbbb-cccc-dddd-000000000091',
    'TIBCO BW App Node Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000092',
    'TIBCO BW App Space Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000093',
    'TIBCO BW CE App Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000094',
    'TIBCO BW CE Version': 'aaaaaaaa-bbbb-cccc-dddd-000000000095',
    'TIBCO BW Domain Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000096',
    'TIBCO BW Engine Property File Path': 'aaaaaaaa-bbbb-cccc-dddd-000000000097',
    'TIBCO BW Property File': 'aaaaaaaa-bbbb-cccc-dddd-000000000098',
    'Varnish Instance Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000099',
    'VMWare Data Center Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000100',
    'VMWare VM Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000101',
    'Web Application ID': 'aaaaaaaa-bbbb-cccc-dddd-000000000102',
    'Web Application Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000103',
    'Web Context Root': 'aaaaaaaa-bbbb-cccc-dddd-000000000104',
    'Web Server Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000105',
    'Web Service Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000106',
    'Web Service Namespace': 'aaaaaaaa-bbbb-cccc-dddd-000000000107',
    'WebLogic Cluster': 'aaaaaaaa-bbbb-cccc-dddd-000000000108',
    'WebLogic Domain': 'aaaaaaaa-bbbb-cccc-dddd-000000000109',
    'WebLogic Home': 'aaaaaaaa-bbbb-cccc-dddd-000000000110',
    'WebLogic Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000111',
    'WebSphere Cell': 'aaaaaaaa-bbbb-cccc-dddd-000000000112',
    'WebSphere Cluster': 'aaaaaaaa-bbbb-cccc-dddd-000000000113',
    'WebSphere Node': 'aaaaaaaa-bbbb-cccc-dddd-000000000114',
    'WebSphere Server': 'aaaaaaaa-bbbb-cccc-dddd-000000000115',
}

fixed_request_attribute_ids = {
    # Generic
    'Synthetic': 'aaaaaaaa-bbbb-cccc-dddd-000000000001',
    'Non-Synthetic': 'aaaaaaaa-bbbb-cccc-dddd-000000000002',
    'x-client-ip': 'aaaaaaaa-bbbb-cccc-dddd-000000000003',
    'x-forwarded-host': 'aaaaaaaa-bbbb-cccc-dddd-000000000004',
    'x-forwarded-server': 'aaaaaaaa-bbbb-cccc-dddd-000000000005',
    'content-length': 'aaaaaaaa-bbbb-cccc-dddd-000000000006',
    'content-type': 'aaaaaaaa-bbbb-cccc-dddd-000000000007',
    'x-forwarded-for': 'aaaaaaaa-bbbb-cccc-dddd-000000000008',
    'x-dynatrace': 'aaaaaaaa-bbbb-cccc-dddd-000000000009',
    'x-dynatrace (client-side)': 'aaaaaaaa-bbbb-cccc-dddd-000000000010',
    'Client IP Address': 'aaaaaaaa-bbbb-cccc-dddd-000000000011',
    'User-Agent': 'aaaaaaaa-bbbb-cccc-dddd-000000000012',
    'User Agent Type': 'aaaaaaaa-bbbb-cccc-dddd-000000000013',
    'x-dynatrace-application': 'aaaaaaaa-bbbb-cccc-dddd-000000000014',
    # Non-Generic
    'sm_user': 'aaaaaaaa-bbbb-cccc-dddd-000000000100',
    'Tenable Client IP': 'aaaaaaaa-bbbb-cccc-dddd-000000000102',
    'SOAPAction': 'aaaaaaaa-bbbb-cccc-dddd-000000000103',
    'aspxerrorpath': 'aaaaaaaa-bbbb-cccc-dddd-000000000104',
    'x-dynatrace-test': 'aaaaaaaa-bbbb-cccc-dddd-000000000105',
    'Load Test LSN': 'aaaaaaaa-bbbb-cccc-dddd-000000000106',
    'Load Test LTN': 'aaaaaaaa-bbbb-cccc-dddd-000000000107',
    'Load Test PC': 'aaaaaaaa-bbbb-cccc-dddd-000000000108',
    'Load Test TSN': 'aaaaaaaa-bbbb-cccc-dddd-000000000109',
    'Load Test VU': 'aaaaaaaa-bbbb-cccc-dddd-000000000111',
    # Customer-specific
    'x-callingsystemid': 'aaaaaaaa-bbbb-cccc-dddd-000000000900',
    'eap-requestuuid': 'aaaaaaaa-bbbb-cccc-dddd-000000000901',
    'message (EAP)': 'aaaaaaaa-bbbb-cccc-dddd-000000000902',
    'RequestId': 'aaaaaaaa-bbbb-cccc-dddd-000000000903',
    'x-callingsysteminstance': 'aaaaaaaa-bbbb-cccc-dddd-000000000904',
    'eap-requestgroupid': 'aaaaaaaa-bbbb-cccc-dddd-000000000905',
    'x-ibm-client-id': 'aaaaaaaa-bbbb-cccc-dddd-000000000906',
}

fixed_request_naming_rules_ids = {
    'Health Check Request (URLs)': 'aaaaaaaa-bbbb-cccc-dddd-000000000001',
    'Health Check Request (User Agent)': 'aaaaaaaa-bbbb-cccc-dddd-000000000002',
    'Tenable Request': 'aaaaaaaa-bbbb-cccc-dddd-000000000100',
}

fixed_conditional_naming_rules_ids = {
    'Shorten Host Name and Add Host Group': 'aaaaaaaa-bbbb-cccc-dddd-000000000001',
    'Shorten Host Name': 'aaaaaaaa-bbbb-cccc-dddd-000000000002',
    'Append Host Group To Host': 'aaaaaaaa-bbbb-cccc-dddd-000000000003',
    'Append Host Group To Process Group': 'aaaaaaaa-bbbb-cccc-dddd-000000000004',
    'Append Host Group - Non-K8s': 'aaaaaaaa-bbbb-cccc-dddd-000000000005',
    'Prepend Namespace to Process Group - K8s': 'aaaaaaaa-bbbb-cccc-dddd-000000000006',
    'Append Host Group To Service': 'aaaaaaaa-bbbb-cccc-dddd-000000000007',
    'Prepend Namespace to Service - K8s': 'aaaaaaaa-bbbb-cccc-dddd-000000000008',
}


def process():
    # For when everything is commented out below...
    pass

    put_request_attribute('x-dynatrace (client-side)', 'REQUEST_HEADER', 'x-dynatrace')
    put_request_attribute('x-dynatrace', 'REQUEST_HEADER', 'x-dynatrace')


    # process_current_customer_specific_auto_tags()

    # Run a sanity test, if pointed to 'Personal' or 'Demo' environment only
    # sanity_test()

    # Test other methods not covered by "sanity_test()"
    # post_web_application('Test Web App')
    # dump_json('/api/config/v1/autoTags', 'aaaaaaaa-bbbb-cccc-dddd-000000000001')
    # add_database_relationship_entity_selector_to_tag('aaaaaaaa-bbbb-cccc-dddd-000000000077', 'OS', 'Tag')

    # Customer2-specific process
    # process_auto_tags_kubernetes()
    # process_auto_tags_azure()

    # Random Personal processes
    # process_all_request_attributes()

    # Safety Exit
    print('Safety Exit!')
    exit(1234)

    # Usage Examples

    # You might want to start with creating all supported auto tags
    # process_all_auto_tags()

    # You might want to clone "process_all_auto_tags()" to create a customer specific version to run
    # process_customer_specific_auto_tags()

    # Create all possible auto tags
    # process_all_request_attributes()

    # wait for eventual consistency...request attributes are referenced by request naming rules
    # time.sleep(30)

    # Create all supported request naming rules
    # process_all_request_naming_rules()
    # process_all_conditional_naming_rules()

    # Create health check request naming rules
    # put_health_check_request_naming_rules_user_agent()
    # put_health_check_request_naming_rules_urls()

    # Create management zones based on AWS integration names
    # post_management_zone_per_aws_credential_name()

    # Report all entities with fixed IDs
    # print("Entities with fixed ids:")
    # report_fixed_id_entities()

    # Report some request naming rules
    # dump_request_naming_rules_rules()
    # endpoint = '/api/config/v1/service/requestNaming'
    # print(get_by_object_id(endpoint, 'aaaaaaaa-bbbb-cccc-dddd-000000000001'))
    # print(get_by_object_id(endpoint, 'aaaaaaaa-bbbb-cccc-dddd-000000000002'))
    # print(get_by_object_id(endpoint, 'aaaaaaaa-bbbb-cccc-dddd-000000000100'))

    # For extra safety
    exit(8000)

    # Dangerous!
    # Delete all previously created entities with "fixed ids" by type
    # delete_auto_tags_with_fixed_ids()
    # delete_request_attributes_with_fixed_ids()
    # delete_request_naming_rules_with_fixed_ids()
    # delete_conditional_naming_rules_with_fixed_ids()

    # Most Dangerous!
    # Delete all possible previously created entities with "fixed ids"
    # delete_all_entities_with_fixed_ids()


def sanity_test():
    # Safety Check
    if env_name not in ['Personal', 'Demo']:
        print('Error in "sanity_test()" method')
        print('Not for use in this environment')
        print('Env: ' + env)
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_line_number())

    print('Entities with fixed ids:')
    report_fixed_id_entities()
    confirm('Are you sure you want to delete all the fixed id entities?')
    delete_all_entities_with_fixed_ids()
    confirm('Do you want to create all auto tags?')
    process_all_auto_tags()
    confirm('Do you want to create all request attributes?')
    process_all_request_attributes()
    # wait for eventual consistency...request attributes are referenced by request naming rules
    print('Sleeping for 10 seconds to allow for eventual consistency...')
    time.sleep(10)
    confirm('Do you want to create all request naming rules?')
    process_all_request_naming_rules()
    confirm('Do you want to create all conditional naming rules?')
    process_all_conditional_naming_rules()


def process_current_customer_specific_auto_tags():
    ###################################################################################################################
    # current_customer_specific: Auto Tags
    ###################################################################################################################
    pass
    # put_request_attribute('User-Agent', 'REQUEST_HEADER', 'User-Agent')
    # put_request_attribute_with_value_processing_control('User Agent Type', 'REQUEST_HEADER', 'User-Agent', {'extractSubstring': {'delimiter': '/', 'position': 'BEFORE'}, 'splitAt': '', 'trim': False})
    # put_request_attribute_tenable_client_ip()
    # put_health_check_request_naming_rules_user_agent()
    # put_health_check_request_naming_rules_urls()
    # put_request_attribute_with_value_processing_control('Non-Synthetic', 'REQUEST_HEADER', 'User-Agent', {'splitAt': '', 'trim': False, 'valueCondition': {'negate': True, 'operator': 'BEGINS_WITH', 'value': 'DynatraceSynthetic'}})
    # put_request_attribute_with_value_processing_control('Synthetic', 'REQUEST_HEADER', 'User-Agent', {'splitAt': '', 'trim': False, 'valueCondition': {'negate': False, 'operator': 'BEGINS_WITH', 'value': 'DynatraceSynthetic'}})


def process_customer_specific_auto_tags():
    ###################################################################################################################
    # customer_specific: Auto Tags
    ###################################################################################################################
    process_auto_tags_basics()
    process_auto_tags_host()
    process_auto_tags_process()
    process_auto_tags_service()
    process_auto_tags_database()
    process_auto_tags_aws()
    process_auto_tags_kubernetes()
    process_auto_tags_java()
    process_auto_tags_springboot()
    process_auto_tags_tomcat()
    process_auto_tags_nodejs()
    process_auto_tags_apache_http()
    process_auto_tags_iis()
    process_auto_tags_dotnet()
    process_auto_tags_websphere()
    process_auto_tags_weblogic()
    process_auto_tags_iib()
    print('customer_specific Auto Tags Complete')


def process_all_auto_tags():
    ###################################################################################################################
    # All Auto Tags
    ###################################################################################################################
    process_auto_tags_basics()
    process_auto_tags_host()
    process_auto_tags_process()
    process_auto_tags_service()
    process_auto_tags_database()
    process_auto_tags_aws()
    process_auto_tags_kubernetes()
    process_auto_tags_java()
    process_auto_tags_springboot()
    process_auto_tags_tomcat()
    process_auto_tags_nodejs()
    process_auto_tags_apache_http()
    process_auto_tags_iis()
    process_auto_tags_dotnet()
    process_auto_tags_websphere()
    process_auto_tags_weblogic()
    process_auto_tags_iib()
    process_auto_tags_cold_fusion()
    process_auto_tags_hybris()
    process_auto_tags_software_ag()
    process_auto_tags_tibco()
    process_auto_tags_cloud_foundry()
    process_auto_tags_apache_spark()
    process_auto_tags_cassandra()
    process_auto_tags_elastic_search()
    process_auto_tags_equinox()
    process_auto_tags_glassfish()
    process_auto_tags_google_cloud_platform()
    process_auto_tags_ibm_cics()
    process_auto_tags_ibm_ims()
    process_auto_tags_php()
    process_auto_tags_ruby()
    process_auto_tags_varnish()
    print('All Auto Tags Complete')


def process_all_request_attributes():
    put_request_attribute('Client IP Address', 'CLIENT_IP', None)
    put_request_attribute('SOAPAction', 'REQUEST_HEADER', 'SOAPAction')
    put_request_attribute('User-Agent', 'REQUEST_HEADER', 'User-Agent')
    put_request_attribute('aspxerrorpath', 'REQUEST_HEADER', 'aspxerrorpath')
    put_request_attribute('content-length', 'REQUEST_HEADER', 'content-length')
    put_request_attribute('content-type', 'REQUEST_HEADER', 'content-type')
    put_request_attribute('eap-requestgroupid', 'REQUEST_HEADER', 'eap-requestgroupid')
    put_request_attribute('eap-requestuuid', 'REQUEST_HEADER', 'eap-requestuuid')
    put_request_attribute('message (EAP)', 'REQUEST_HEADER', 'message')
    put_request_attribute('sm_user', 'REQUEST_HEADER', 'sm_user')
    put_request_attribute('x-callingsystemid', 'REQUEST_HEADER', 'x-callingsystemid')
    put_request_attribute('x-callingsysteminstance', 'REQUEST_HEADER', 'x-callingsysteminstance')
    put_request_attribute('x-client-ip', 'REQUEST_HEADER', 'x-client-ip')
    put_request_attribute('x-dynatrace (client-side)', 'REQUEST_HEADER', 'x-dynatrace')
    put_request_attribute('x-dynatrace', 'REQUEST_HEADER', 'x-dynatrace')
    put_request_attribute('x-dynatrace-application', 'REQUEST_HEADER', 'x-dynatrace-application')
    put_request_attribute('x-forwarded-for', 'REQUEST_HEADER', 'x-forwarded-for')
    put_request_attribute('x-forwarded-host', 'REQUEST_HEADER', 'x-forwarded-host')
    put_request_attribute('x-forwarded-server', 'REQUEST_HEADER', 'x-forwarded-server')
    put_request_attribute('x-ibm-client-id', 'REQUEST_HEADER', 'x-ibm-client-id')

    put_request_attribute_request_id()
    put_request_attribute_tenable_client_ip()

    put_request_attribute_with_value_processing_control('Non-Synthetic', 'REQUEST_HEADER', 'User-Agent', {'splitAt': '', 'trim': False, 'valueCondition': {'negate': True, 'operator': 'BEGINS_WITH', 'value': 'DynatraceSynthetic'}})
    put_request_attribute_with_value_processing_control('Synthetic', 'REQUEST_HEADER', 'User-Agent', {'splitAt': '', 'trim': False, 'valueCondition': {'negate': False, 'operator': 'BEGINS_WITH', 'value': 'DynatraceSynthetic'}})
    put_request_attribute_with_value_processing_control('User Agent Type', 'REQUEST_HEADER', 'User-Agent', {'extractSubstring': {'delimiter': '/', 'position': 'BEFORE'}, 'splitAt': '', 'trim': False})

    # Request Attributes for Load Testing
    put_request_attribute('x-dynatrace-test', 'REQUEST_HEADER', 'x-dynatrace-test')
    put_request_attribute_load_testing('Load Test LSN', 'REQUEST_HEADER', 'x-dynatrace-test', 'LSN=', ';', 'BETWEEN')
    put_request_attribute_load_testing('Load Test LTN', 'REQUEST_HEADER', 'x-dynatrace-test', 'LTN=', ';', 'BETWEEN')
    put_request_attribute_load_testing('Load Test PC', 'REQUEST_HEADER', 'x-dynatrace-test', 'PC=', ';', 'BETWEEN')
    put_request_attribute_load_testing('Load Test TSN', 'REQUEST_HEADER', 'x-dynatrace-test', 'TSN=', ';', 'BETWEEN')
    put_request_attribute_load_testing('Load Test VU', 'REQUEST_HEADER', 'x-dynatrace-test', 'VU=', ';', 'BETWEEN')


def process_all_request_naming_rules():
    put_tenable_request_naming_rules()
    put_health_check_request_naming_rules_user_agent()
    put_health_check_request_naming_rules_urls()


def process_all_conditional_naming_rules():
    put_conditional_naming_rules('host', 'Shorten Host Name and Add Host Group', 'HOST_GROUP_NAME', '{Host:DetectedName/([^\\.]*+)} {HostGroup:Name}')
    put_conditional_naming_rules('host', 'Shorten Host Name', 'HOST_GROUP_NAME', '{Host:DetectedName/([^\\.]*+)}')
    put_conditional_naming_rules('host', 'Append Host Group To Host', 'HOST_GROUP_NAME', '{Host:DetectedName} {HostGroup:Name}')
    put_conditional_naming_rules('processGroup', 'Append Host Group To Process Group', 'HOST_GROUP_NAME', '{ProcessGroup:DetectedName} - {HostGroup:Name}')
    put_conditional_naming_rules_non_k8s('processGroup', 'Append Host Group - Non-K8s', 'HOST_GROUP_NAME', '{ProcessGroup:DetectedName} - {HostGroup:Name}')
    put_conditional_naming_rules_k8s('processGroup', 'Prepend Namespace to Process Group - K8s', '{ProcessGroup:KubernetesNamespace} -{ProcessGroup:DetectedName}')
    put_conditional_naming_rules('service', 'Append Host Group To Service', 'HOST_GROUP_NAME', '{Service:DetectedName} - {HostGroup:Name}')
    put_conditional_naming_rules_k8s('service', 'Prepend Namespace to Service - K8s', '{ProcessGroup:KubernetesNamespace} -{Service:DetectedName}')


def process_auto_tags_basics():
    # Basic Tags
    put_auto_tag('Host Name', 'HOST_NAME', 'EXISTS', '{Host:DetectedName}', 'HOST')
    put_auto_tag('IP Address', 'HOST_IP_ADDRESS', 'EXISTS', '{Host:IpAddress}', 'HOST')
    put_auto_tag('Service Name', 'SERVICE_NAME', 'EXISTS', '{Service:DetectedName}', 'SERVICE')
    put_auto_tag('Web Application Name', 'WEB_APPLICATION_NAME', 'EXISTS', '{WebApplication:Name}', 'APPLICATION')
    put_auto_tag_with_propagation_types('Process Group Name', 'PROCESS_GROUP_NAME', 'EXISTS', '{ProcessGroup:DetectedName}', 'PROCESS_GROUP', ['PROCESS_GROUP_TO_SERVICE'])

    # "Special" Best Practice Tags
    put_auto_tag_host_group()
    put_auto_tag_cloud_provider()
    put_auto_tag_os('OS', ['AIX', 'Darwin', 'HPUX', 'Linux', 'Solaris', 'Windows', 'zOS'])

    # "Special" Tags: Location-oriented
    put_auto_tag('Geolocation', 'OPENSTACK_REGION_NAME', 'EXISTS', '{GeolocationSite:Name}', 'PROCESS_GROUP')
    put_auto_tag_aws_region()
    put_auto_tag_data_center()

    # "Special" Tags: Miscellaneous
    put_auto_tag_service_topology_type()
    put_auto_tag_process_technology()


def process_auto_tags_host():
    put_auto_tag('Host CPU Cores', 'HOST_DETECTED_NAME', 'EXISTS', '{Host:CpuCores}', 'HOST')
    put_auto_tag('VMWare Data Center Name', 'VMWARE_DATACENTER_NAME', 'EXISTS', '{VmwareDatacenter:Name}', 'HOST')
    put_auto_tag('VMWare VM Name', 'VMWARE_VM_NAME', 'EXISTS', '{VmwareVm:Name}', 'HOST')
    put_auto_tag_host_technology()


def process_auto_tags_process():
    put_auto_tag_typical_process_group_dynamic_key('Command Line Args', 'COMMAND_LINE_ARGS', '{ProcessGroup:CommandLineArgs}')
    put_auto_tag_typical_process_group_dynamic_key('Exe Name', 'EXE_NAME', '{ProcessGroup:ExeName}')
    put_auto_tag_typical_process_group_dynamic_key('Exe Path', 'EXE_PATH', '{ProcessGroup:ExePath}')


def process_auto_tags_service():
    put_auto_tag('Web Application ID', 'SERVICE_WEB_APPLICATION_ID', 'EXISTS', '{Service:WebApplicationId}', 'SERVICE')
    put_auto_tag('Web Context Root', 'SERVICE_WEB_CONTEXT_ROOT', 'EXISTS', '{Service:WebContextRoot}', 'SERVICE')
    put_auto_tag('Web Server Name', 'SERVICE_WEB_SERVER_NAME', 'EXISTS', '{Service:WebServerName}', 'SERVICE')
    put_auto_tag('Web Service Namespace', 'SERVICE_WEB_SERVICE_NAME', 'EXISTS', '{Service:WebServiceNamespace}', 'SERVICE')
    put_auto_tag('Web Service Name', 'SERVICE_WEB_SERVICE_NAMESPACE', 'EXISTS', '{Service:WebServiceName}', 'SERVICE')


def process_auto_tags_database():
    put_auto_tag('Database Vendor', 'SERVICE_DATABASE_VENDOR', 'EXISTS', '{Service:DatabaseVendor}', 'SERVICE')
    put_auto_tag_typical_process_group_dynamic_key('Oracle SID', 'ORACLE_SID', '{ProcessGroup:OracleSid}')
    put_auto_tag_typical_process_group_dynamic_key('MS SQL Instance Name', 'MSSQL_INSTANCE_NAME', '{ProcessGroup:MssqlInstanceName}')


def process_auto_tags_aws():
    put_auto_tag('AWS Availability Zone', 'AWS_AVAILABILITY_ZONE_NAME', 'EXISTS', '{AwsAvailabilityZone:Name}', 'PROCESS_GROUP')
    put_auto_tag_typical_process_group_dynamic_key('Amazon ECR Image Account Id', 'AMAZON_ECR_IMAGE_ACCOUNT_ID', '{ProcessGroup:AmazonECRImageAccountId}')
    put_auto_tag_typical_process_group_dynamic_key('Amazon ECR Image Region', 'AMAZON_ECR_IMAGE_REGION', '{ProcessGroup:AmazonECRImageRegion}')
    put_auto_tag_typical_process_group_dynamic_key('Amazon ECS Cluster', 'AWS_ECS_CLUSTER', '{ProcessGroup:AmazonECSCluster}')
    put_auto_tag_typical_process_group_dynamic_key('Amazon ECS Container Name', 'AWS_ECS_CONTAINERNAME', '{ProcessGroup:AmazonECSContainerName}')
    put_auto_tag_typical_process_group_dynamic_key('Amazon ECS Family', 'AWS_ECS_FAMILY', '{ProcessGroup:AmazonECSFamily}')
    put_auto_tag_typical_process_group_dynamic_key('Amazon ECS Revision', 'AWS_ECS_REVISION', '{ProcessGroup:AmazonECSRevision}')
    put_auto_tag_typical_process_group_dynamic_key('Amazon Lambda Function Name', 'AMAZON_LAMBDA_FUNCTION_NAME', '{ProcessGroup:AmazonLambdaFunctionName}')
    # TODO: Cannot use lambda region, region placeholder not working, use AWS AZ exists and regex extract maybe (later)
    # put_auto_tag_typical_process_group_dynamic_key('Amazon Region', 'AMAZON_REGION', '{ProcessGroup:AmazonRegion}')


def process_auto_tags_azure():
    put_auto_tag('Azure Region', 'AZURE_REGION_NAME', 'EXISTS', '{AzureRegion:Name}', 'PROCESS_GROUP')
    put_auto_tag('Azure Site Name', 'PROCESS_GROUP_AZURE_SITE_NAME', 'EXISTS', '{ProcessGroup:AzureSiteName}', 'PROCESS_GROUP')
    put_auto_tag('Azure Scale Set', 'AZURE_SCALE_SET_NAME', 'EXISTS', '{AzureScaleSet:Name}', 'PROCESS_GROUP')


def process_auto_tags_kubernetes():
    put_auto_tag('Kubernetes Cluster', 'KUBERNETES_CLUSTER_NAME', 'EXISTS', '{KubernetesCluster:Name}', 'PROCESS_GROUP')
    put_auto_tag_typical_process_group_dynamic_key('Kubernetes Base Pod Name', 'KUBERNETES_BASE_POD_NAME', '{ProcessGroup:KubernetesBasePodName}')
    put_auto_tag_typical_process_group_dynamic_key('Kubernetes Container Name', 'KUBERNETES_CONTAINER_NAME', '{ProcessGroup:KubernetesContainerName}')
    put_auto_tag_typical_process_group_dynamic_key('Kubernetes Full Pod Name', 'KUBERNETES_FULL_POD_NAME', '{ProcessGroup:KubernetesFullPodName}')
    put_auto_tag_typical_process_group_dynamic_key('Kubernetes Namespace', 'KUBERNETES_NAMESPACE', '{ProcessGroup:KubernetesNamespace}')
    put_auto_tag_typical_process_group_dynamic_key('Kubernetes Pod UID', 'KUBERNETES_POD_UID', '{ProcessGroup:KubernetesPodUid}')


def process_auto_tags_java():
    put_auto_tag_typical_process_group_dynamic_key('Java Jar File', 'JAVA_JAR_FILE', '{ProcessGroup:JavaJarFile}')
    put_auto_tag_typical_process_group_dynamic_key('Java Jar Path', 'JAVA_JAR_PATH', '{ProcessGroup:JavaJarPath}')


def process_auto_tags_springboot():
    put_auto_tag_typical_process_group_dynamic_key('SpringBootAppName', 'SPRINGBOOT_APP_NAME', '{ProcessGroup:SpringBootAppName}')
    put_auto_tag_typical_process_group_dynamic_key('SpringBootProfileName', 'SPRINGBOOT_PROFILE_NAME', '{ProcessGroup:SpringBootProfileName}')
    put_auto_tag_typical_process_group_dynamic_key('SpringBootStartupClass', 'SPRINGBOOT_STARTUP_CLASS', '{ProcessGroup:SpringBootStartupClass}')


def process_auto_tags_tomcat():
    put_auto_tag_typical_process_group_dynamic_key('Catalina Base', 'CATALINA_BASE', '{ProcessGroup:CatalinaBase}')
    put_auto_tag_typical_process_group_dynamic_key('Catalina Home', 'CATALINA_HOME', '{ProcessGroup:CatalinaHome}')


def process_auto_tags_nodejs():
    put_auto_tag_typical_process_group_dynamic_key('Node JS Script Name', 'NODE_JS_SCRIPT_NAME', '{ProcessGroup:NodeJsScriptName}')
    put_auto_tag_typical_process_group_dynamic_key('NodeJS App Base Director', 'NODE_JS_APP_BASE_DIRECTORY', '{ProcessGroup:NodeJsAppBaseDirectory}')
    put_auto_tag_typical_process_group_dynamic_key('NodeJS App Name', 'NODE_JS_APP_NAME', '{ProcessGroup:NodeJsAppName}')


def process_auto_tags_apache_http():
    put_auto_tag_typical_process_group_dynamic_key('Apache Config Path', 'APACHE_CONFIG_PATH', '{ProcessGroup:ApacheConfigPath}')


def process_auto_tags_iis():
    put_auto_tag_typical_process_group_dynamic_key('IIS App Pool', 'IIS_APP_POOL', '{ProcessGroup:IISAppPool}')
    put_auto_tag_typical_process_group_dynamic_key('IIS Role Name', 'IIS_ROLE_NAME', '{ProcessGroup:IISRoleName}')


def process_auto_tags_dotnet():
    put_auto_tag_typical_process_group_dynamic_key('Asp Dot Net Core Application Path', 'ASP_DOT_NET_CORE_APPLICATION_PATH', '{ProcessGroup:AspDotNetCoreApplicationPath}')
    put_auto_tag_typical_process_group_dynamic_key('Dot Net Command Path', 'DOTNET_COMMAND_PATH', '{ProcessGroup:DotNetCommandPath}')
    put_auto_tag_typical_process_group_dynamic_key('Dot Net Command', 'DOTNET_COMMAND', '{ProcessGroup:DotNetCommand}')


def process_auto_tags_websphere():
    put_auto_tag_typical_process_group_dynamic_key('WebSphere Cell', 'WEB_SPHERE_CELL_NAME', '{ProcessGroup:WebSphereCellName}')
    put_auto_tag_typical_process_group_dynamic_key('WebSphere Cluster', 'WEB_SPHERE_CLUSTER_NAME', '{ProcessGroup:WebSphereClusterName}')
    put_auto_tag_typical_process_group_dynamic_key('WebSphere Node', 'WEB_SPHERE_NODE_NAME', '{ProcessGroup:WebSphereNodeName}')
    put_auto_tag_typical_process_group_dynamic_key('WebSphere Server', 'WEB_SPHERE_SERVER_NAME', '{ProcessGroup:WebSphereServerName}')


def process_auto_tags_weblogic():
    put_auto_tag_typical_process_group_dynamic_key('WebLogic Cluster', 'WEB_LOGIC_CLUSTER_NAME', '{ProcessGroup:WebLogicClusterName}')
    put_auto_tag_typical_process_group_dynamic_key('WebLogic Domain', 'WEB_LOGIC_DOMAIN_NAME', '{ProcessGroup:WebLogicDomainName}')
    put_auto_tag_typical_process_group_dynamic_key('WebLogic Home', 'WEB_LOGIC_HOME', '{ProcessGroup:WebLogicHome}')
    put_auto_tag_typical_process_group_dynamic_key('WebLogic Name', 'WEB_LOGIC_NAME', '{ProcessGroup:WebLogicName}')


def process_auto_tags_iib():
    put_auto_tag_typical_process_group_dynamic_key('IBM Integration Node Name', 'IBM_INTEGRATION_NODE_NAME', '{ProcessGroup:IBMIntegrationNodeName}')
    put_auto_tag_typical_process_group_dynamic_key('IBM Integration Server Name', 'IBM_INTEGRATION_SERVER_NAME', '{ProcessGroup:IBMIntegrationServerName}')
    # {Service:IIBApplicationName}: does not seem to be valid placeholder in UI


def process_auto_tags_cold_fusion():
    put_auto_tag_typical_process_group_dynamic_key('Cold Fusion Jvm Config File', 'COLDFUSION_JVM_CONFIG_FILE', '{ProcessGroup:ColdFusionJvmConfigFile}')
    put_auto_tag_typical_process_group_dynamic_key('Cold Fusion Service Name', 'COLDFUSION_SERVICE_NAME', '{ProcessGroup:ColdFusionServiceName}')


def process_auto_tags_hybris():
    put_auto_tag_typical_process_group_dynamic_key('Hybris Bin Directory', 'HYBRIS_BIN_DIRECTORY', '{ProcessGroup:HybrisBinDirectory}')
    put_auto_tag_typical_process_group_dynamic_key('Hybris Config Directory', 'HYBRIS_CONFIG_DIRECTORY', '{ProcessGroup:HybrisConfigDirectory}')
    put_auto_tag_typical_process_group_dynamic_key('Hybris Data Directory', 'HYBRIS_DATA_DIRECTORY', '{ProcessGroup:HybrisDataDirectory}')


def process_auto_tags_software_ag():
    put_auto_tag_typical_process_group_dynamic_key('Software AG Install Root', 'SOFTWAREAG_INSTALL_ROOT', '{ProcessGroup:SoftwareAGInstallRoot}')
    put_auto_tag_typical_process_group_dynamic_key('Software AG Product Property Name', 'SOFTWAREAG_PRODUCTPROPNAME', '{ProcessGroup:SoftwareAGProductPropertyName}')


def process_auto_tags_tibco():
    put_auto_tag_typical_process_group_dynamic_key('TIBCO BW App Node Name', 'TIBCO_BUSINESS_WORKS_APP_NODE_NAME', '{ProcessGroup:TIBCOBusinessWorksAppNodeName}')
    put_auto_tag_typical_process_group_dynamic_key('TIBCO BW App Space Name', 'TIBCO_BUSINESS_WORKS_APP_SPACE_NAME', '{ProcessGroup:TIBCOBusinessWorksAppSpaceName}')
    put_auto_tag_typical_process_group_dynamic_key('TIBCO BW CE App Name', 'TIBCO_BUSINESSWORKS_CE_APP_NAME', '{ProcessGroup:TIBCOBusinessWorksCeAppName}')
    put_auto_tag_typical_process_group_dynamic_key('TIBCO BW CE Version', 'TIBCO_BUSINESSWORKS_CE_VERSION', '{ProcessGroup:TIBCOBusinessWorksCeVersion}')
    put_auto_tag_typical_process_group_dynamic_key('TIBCO BW Domain Name', 'TIBCO_BUSINESS_WORKS_DOMAIN_NAME', '{ProcessGroup:TIBCOBusinessWorksDomainName}')
    put_auto_tag_typical_process_group_dynamic_key('TIBCO BW Engine Property File Path', 'TIBCO_BUSINESS_WORKS_ENGINE_PROPERTY_FILE_PATH', '{ProcessGroup:TIBCOBusinessWorksEnginePropertyFilePath}')
    put_auto_tag_typical_process_group_dynamic_key('TIBCO BW Property File', 'TIBCO_BUSINESS_WORKS_ENGINE_PROPERTY_FILE', '{ProcessGroup:TIBCOBusinessWorksEnginePropertyFile}')
    put_auto_tag_typical_process_group_dynamic_key('TIBCO Business Works Home', 'TIBCO_BUSINESS_WORKS_HOME', '{ProcessGroup:TIBCOBusinessWorksHome}')


def process_auto_tags_cloud_foundry():
    put_auto_tag_typical_process_group_dynamic_key('Cloud Foundry App Id', 'CLOUD_FOUNDRY_APP_ID', '{ProcessGroup:CloudFoundryAppId}')
    put_auto_tag_typical_process_group_dynamic_key('Cloud Foundry App Name', 'CLOUD_FOUNDRY_APP_NAME', '{ProcessGroup:CloudFoundryAppName}')
    put_auto_tag_typical_process_group_dynamic_key('Cloud Foundry Instance Index', 'CLOUD_FOUNDRY_INSTANCE_INDEX', '{ProcessGroup:CloudFoundryInstanceIndex}')
    put_auto_tag_typical_process_group_dynamic_key('Cloud Foundry Space Id', 'CLOUD_FOUNDRY_SPACE_ID', '{ProcessGroup:CloudFoundrySpaceId}')
    put_auto_tag_typical_process_group_dynamic_key('Cloud Foundry Space Name', 'CLOUD_FOUNDRY_SPACE_NAME', '{ProcessGroup:CloudFoundrySpaceName}')


def process_auto_tags_apache_spark():
    put_auto_tag_typical_process_group_dynamic_key('Apache Spark Master Ip Address', 'APACHE_SPARK_MASTER_IP_ADDRESS', '{ProcessGroup:ApacheSparkMasterIpAddress}')


def process_auto_tags_cassandra():
    put_auto_tag_typical_process_group_dynamic_key('Cassandra Cluster Name', 'CASSANDRA_CLUSTER_NAME', '{ProcessGroup:CassandraClusterName}')


def process_auto_tags_elastic_search():
    put_auto_tag_typical_process_group_dynamic_key('Elasticsearch Cluster Name', 'ELASTICSEARCH_CLUSTER_NAME', '{ProcessGroup:ElasticsearchClusterName}')
    put_auto_tag_typical_process_group_dynamic_key('Elasticsearch Node Name', 'ELASTICSEARCH_NODE_NAME', '{ProcessGroup:ElasticsearchNodeName}')


def process_auto_tags_equinox():
    put_auto_tag_typical_process_group_dynamic_key('Equinox Config Path', 'EQUINOX_CONFIG_PATH', '{ProcessGroup:EquinoxConfigPath}')


def process_auto_tags_glassfish():
    put_auto_tag_typical_process_group_dynamic_key('GlassFish Domain Name', 'GLASS_FISH_DOMAIN_NAME', '{ProcessGroup:GlassFishDomainName}')
    put_auto_tag_typical_process_group_dynamic_key('GlassFish Instance Name', 'GLASS_FISH_INSTANCE_NAME', '{ProcessGroup:GlassFishInstanceName}')


def process_auto_tags_google_cloud_platform():
    put_auto_tag_typical_process_group_dynamic_key('Google App Engine Instance', 'GOOGLE_APP_ENGINE_INSTANCE', '{ProcessGroup:GoogleAppEngineInstance}')
    put_auto_tag_typical_process_group_dynamic_key('Google App Engine Service', 'GOOGLE_APP_ENGINE_SERVICE', '{ProcessGroup:GoogleAppEngineService}')
    put_auto_tag_typical_process_group_dynamic_key('Google Cloud Project', 'GOOGLE_CLOUD_PROJECT', '{ProcessGroup:GoogleCloudProject}')


def process_auto_tags_ibm_cics():
    put_auto_tag_typical_process_group_dynamic_key('IBM CICS Region', 'IBM_CICS_REGION', '{ProcessGroup:IBMCicsRegion}')
    # This one is broken now, so skip it.
    # put_auto_tag_typical_process_group_dynamic_key('IBM CTG Name', 'IBM_CTG_NAME', '{ProcessGroup:IBMCtgName}')


def process_auto_tags_ibm_ims():
    put_auto_tag_typical_process_group_dynamic_key('IBM IMS Connect Region', 'IBM_IMS_CONNECT_REGION', '{ProcessGroup:IBMImsConnectRegion}')
    put_auto_tag_typical_process_group_dynamic_key('IBM IMS Control Region', 'IBM_IMS_CONTROL_REGION', '{ProcessGroup:IBMImsControlRegion}')
    put_auto_tag_typical_process_group_dynamic_key('IBM IMS Message Processing Region', 'IBM_IMS_MESSAGE_PROCESSING_REGION', '{ProcessGroup:IBMImsMessageProcessingRegion}')
    put_auto_tag_typical_process_group_dynamic_key('IBM IMS Soap GW Name', 'IBM_IMS_SOAP_GW_NAME', '{ProcessGroup:IBMImsSoapGwName}')


def process_auto_tags_php():
    put_auto_tag_typical_process_group_dynamic_key('PHP Script Path', 'PHP_SCRIPT_PATH', '{ProcessGroup:PHPScriptPath}')
    put_auto_tag_typical_process_group_dynamic_key('PHP Working Directory', 'PHP_WORKING_DIRECTORY', '{ProcessGroup:PHPWorkingDirectory}')


def process_auto_tags_ruby():
    put_auto_tag_typical_process_group_dynamic_key('Ruby App Root Path', 'RUBY_APP_ROOT_PATH', '{ProcessGroup:RubyAppRootPath}')
    put_auto_tag_typical_process_group_dynamic_key('Ruby Script Path', 'RUBY_SCRIPT_PATH', '{ProcessGroup:RubyScriptPath}')


def process_auto_tags_varnish():
    put_auto_tag_typical_process_group_dynamic_key('Varnish Instance Name', 'VARNISH_INSTANCE_NAME', '{ProcessGroup:VarnishInstanceName}')


def put(endpoint, object_id, payload):
    # In general, favor put over post so "fixed ids" can be used
    # print(endpoint, object_id, payload)
    if endpoint == '/api/config/v1/service/requestNaming':
        name = json.loads(payload).get('namingPattern')
    else:
        if endpoint.startswith('/api/config/v1/conditionalNaming/'):
            name = json.loads(payload).get('displayName')
        else:
            name = json.loads(payload).get('name')

    json_data = json.dumps(json.loads(payload), indent=4, sort_keys=False)

    r = dynatrace_api.put(env, token, endpoint, object_id, json_data.encode('utf-8'))

    if r.status_code == 201:
        print('Added ' + name + ': ' + object_id + ' (' + endpoint + ')')
    else:
        if r.status_code == 204:
            print('Updated ' + name + ': ' + object_id + ' (' + endpoint + ')')


def post(endpoint: str, payload: str) -> Response:
    r = dynatrace_api.post(env, token, endpoint, payload)
    return r


def delete(endpoint, object_id):
    r = dynatrace_api.delete(env, token, endpoint, object_id)
    print(f'Deleted {object_id} ({endpoint}')
    return r


def post_management_zone_per_aws_credential_name():
    endpoint = '/api/config/v1/aws/credentials'
    r = get_object_list(endpoint)
    aws_credentials_json = json.loads(r.text)
    for aws_credential in aws_credentials_json:
        aws_credential_name = aws_credential.get('name')
        post_management_zone_aws_credential_name(aws_credential_name)


def post_management_zone_aws_credential_name(aws_credential_name):
    mz_name = 'ZZ AWS:' + aws_credential_name

    entity_selector_based_rules = []

    entity_selectors = [
        'type(EC2_INSTANCE),fromRelationships.isAccessibleBy(type(AWS_CREDENTIALS),entityName.equals("' + aws_credential_name + '"))',
        'type(PROCESS_GROUP),fromRelationships.runsOn(type(HOST),fromRelationships.runsOn(type(EC2_INSTANCE),fromRelationships.isAccessibleBy(type(AWS_CREDENTIALS),,entityName.equals("' + aws_credential_name + '"))))',
        'type(APPLICATION),fromRelationships.calls(type(SERVICE),fromRelationships.runsOnHost(type(HOST),fromRelationships.runsOn(type(EC2_INSTANCE),fromRelationships.isAccessibleBy(type(AWS_CREDENTIALS),entityName.equals("' + aws_credential_name + '")))))',
        'type(custom_device),fromRelationships.isAccessibleBy(type(aws_credentials),entityName.equals("' + aws_credential_name + '"))',
        'type(SERVICE),fromRelationships.runsOnHost(type(HOST),fromRelationships.runsOn(type(EC2_INSTANCE),fromRelationships.isAccessibleBy(type(AWS_CREDENTIALS),,entityName.equals("' + aws_credential_name + '"))))',
        'type(custom_device_group),fromRelationships.isAccessibleBy(type(aws_credentials),entityName.equals("' + aws_credential_name + '"))',
        'type(PROCESS_GROUP_INSTANCE),fromRelationships.isProcessOf(type(HOST),fromRelationships.runsOn(type(EC2_INSTANCE),fromRelationships.isAccessibleBy(type(AWS_CREDENTIALS),entityName.equals("' + aws_credential_name + '"))))',
        'type(HOST),fromRelationships.runsOn(type(EC2_INSTANCE),fromRelationships.isAccessibleBy(type(AWS_CREDENTIALS),entityName.equals("' + aws_credential_name + '")))'
    ]

    for entity_selector in entity_selectors:
        entity_selector_based_rule = {"enabled": True, "entitySelector": entity_selector}
        entity_selector_based_rules.append(entity_selector_based_rule)

    mz_template = {"name": mz_name, "entitySelectorBasedRules": entity_selector_based_rules, "description": None, "rules": [], "dimensionalRules": []}

    payload = json.dumps(mz_template)

    endpoint = '/api/config/v1/managementZones'

    if offline:
        save('management-zone', mz_name, payload)
    else:
        post(endpoint, payload)


def post_management_zone(mz_name, tags):
    rules = []

    # Process Group Rule
    conditions = []
    for tag in tags:
        tag_key = tag[0]
        tag_value = tag[1]
        conditions.append(build_tag_condition_equality(tag_key, tag_value, 'PROCESS_GROUP_TAGS'))
    rules.append(build_process_group_rule(conditions))

    # Database Service Rule
    conditions = []
    for tag in tags:
        tag_key = tag[0]
        tag_value = tag[1]
        conditions.append(build_tag_condition_equality(tag_key, tag_value, 'SERVICE_TAGS'))
    conditions.append(build_service_type_is_database_condition())
    rules.append(build_database_service_rule(conditions))

    # Browser Monitor Rule
    conditions = []
    for tag in tags:
        tag_key = tag[0]
        tag_value = tag[1]
        conditions.append(build_tag_condition_existence(tag_key, tag_value, 'BROWSER_MONITOR_TAGS'))
    rules.append(build_browser_monitor_rule(conditions))

    # Web Application Rule
    conditions = []
    for tag in tags:
        tag_key = tag[0]
        tag_value = tag[1]
        conditions.append(build_tag_condition_equality(tag_key, tag_value, 'WEB_APPLICATION_TAGS'))
    rules.append(build_web_application_rule(conditions))

    payload = json.dumps({'name': mz_name, 'rules': rules})

    endpoint = '/api/config/v1/managementZones'

    if offline:
        save('management-zone', mz_name, payload)
    else:
        post(endpoint, payload)


def post_management_zone_tag_existence(mz_name, tag_keys, existence):
    # existence: True-Check for Existence, False-Check for Non-Existence
    rules = []

    # Process Group Rule
    conditions = []
    for tag_key in tag_keys:
        conditions.append(build_tag_condition_existence(tag_key, 'PROCESS_GROUP_TAGS', existence))
    rules.append(build_process_group_rule(conditions))
    payload = json.dumps({'name': mz_name, 'rules': rules})
    endpoint = '/api/config/v1/managementZones'
    if offline:
        save('management-zone', mz_name, payload)
    else:
        post(endpoint, payload)


def build_tag_condition_equality(tag_key, tag_value, tag_type):
    # tag_type: PROCESS_GROUP_TAGS|SERVICE_TAGS|BROWSER_MONITOR_TAGS|WEB_APPLICATION_TAGS
    return build_tag_condition(False, 'EQUALS', 'TAG', tag_key, tag_value, tag_type, 'STATIC')


def build_tag_condition_existence(tag_key, tag_type, existence):
    # tag_type: PROCESS_GROUP_TAGS|SERVICE_TAGS|BROWSER_MONITOR_TAGS|WEB_APPLICATION_TAGS
    if existence:
        negate = False
    else:
        negate = True
    return build_tag_condition(negate, 'TAG_KEY_EQUALS', 'TAG', tag_key, None, tag_type, 'STATIC')


def build_service_type_is_database_condition():
    return build_entity_type_condition(False, 'EQUALS', 'SERVICE_TYPE', 'DATABASE_SERVICE', 'SERVICE_TYPE', 'STATIC')


def build_process_group_rule(conditions):
    return build_rule(conditions, True, ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE'], 'PROCESS_GROUP')


def build_database_service_rule(conditions):
    return build_rule(conditions, True, [], 'SERVICE')


def build_browser_monitor_rule(conditions):
    return build_rule(conditions, True, [], 'BROWSER_MONITOR')


def build_web_application_rule(conditions):
    return build_rule(conditions, True, [], 'WEB_APPLICATION')


def build_rule(conditions, enabled, propagation_types, entity_type):
    return {'conditions': conditions, 'enabled': enabled, 'propagationTypes': propagation_types, 'type': entity_type}


def build_tag_condition(negate, operator, comparison_type, tag_key, tag_value, key_attribute, key_type):
    condition_template = {
     'comparisonInfo': {
      'negate': False,
      'operator': 'EQUALS',
      'type': 'TAG',
      'value': {
       'context': 'CONTEXTLESS',
       'key': 'Environment',
       'value': 'DEVELOPMENT'
      }
     },
     'key': {
      'attribute': 'SERVICE_TAGS',
      'type': 'STATIC'
     }
    }

    condition = copy.deepcopy(condition_template)
    condition['comparisonInfo']['negate'] = negate
    condition['comparisonInfo']['operator'] = operator
    condition['comparisonInfo']['type'] = comparison_type
    condition['comparisonInfo']['value']['key'] = tag_key
    if operator != 'EXISTS':
        condition['comparisonInfo']['value']['value'] = tag_value
    condition['key']['attribute'] = key_attribute
    condition['key']['type'] = key_type
    return condition


def build_entity_type_condition(negate, operator, comparison_type, value, key_attribute, key_type):
    condition_template = {
     'comparisonInfo': {
      'negate': False,
      'operator': 'EQUALS',
      'type': 'SERVICE_TYPE',
      'value': 'DATABASE_SERVICE'
     },
     'key': {
      'attribute': 'SERVICE_TYPE',
      'type': 'STATIC'
     }
    }

    condition = copy.deepcopy(condition_template)
    condition['comparisonInfo']['negate'] = negate
    condition['comparisonInfo']['operator'] = operator
    condition['comparisonInfo']['type'] = comparison_type
    condition['comparisonInfo']['value'] = value
    condition['key']['attribute'] = key_attribute
    condition['key']['type'] = key_type
    return condition


def post_web_application_and_detection_rule(web_application_name, domain):
    post_application_detection_rule(post_web_application(web_application_name), domain)


def post_web_application(web_application_name):
    payload = json.dumps(build_web_application(web_application_name))

    endpoint = '/api/config/v1/applications/web'

    # delete(endpoint, 'APPLICATION-6A2835FFE8A33793')
    if offline:
        save('application-web', web_application_name, payload)
        return 'aaaaaaaa-aaaa-aaaa-aaaa-111111111111'
    else:
        r = post(endpoint, payload)
        return json.loads(r.text).get('id')


def build_web_application(name):
    web_application_template = {
        'name': 'NAME',
        'realUserMonitoringEnabled': True,
        'costControlUserSessionPercentage': 100,
        'loadActionKeyPerformanceMetric': 'VISUALLY_COMPLETE',
        'sessionReplayConfig': {
            'enabled': False,
            'costControlPercentage': 100,
            'enableCssResourceCapturing': True,
            'cssResourceCapturingExclusionRules': []
        },
        'xhrActionKeyPerformanceMetric': 'VISUALLY_COMPLETE',
        'loadActionApdexSettings': {
            'toleratedThreshold': 3000,
            'frustratingThreshold': 12000,
            'toleratedFallbackThreshold': 3000,
            'frustratingFallbackThreshold': 12000
        },
        'xhrActionApdexSettings': {
            'toleratedThreshold': 3000,
            'frustratingThreshold': 12000,
            'toleratedFallbackThreshold': 3000,
            'frustratingFallbackThreshold': 12000
        },
        'customActionApdexSettings': {
            'toleratedThreshold': 3000,
            'frustratingThreshold': 12000,
            'toleratedFallbackThreshold': 3000,
            'frustratingFallbackThreshold': 12000
        },
        'waterfallSettings': {
            'uncompressedResourcesThreshold': 860,
            'resourcesThreshold': 100000,
            'resourceBrowserCachingThreshold': 50,
            'slowFirstPartyResourcesThreshold': 200000,
            'slowThirdPartyResourcesThreshold': 200000,
            'slowCdnResourcesThreshold': 200000,
            'speedIndexVisuallyCompleteRatioThreshold': 50
        },
        'monitoringSettings': {
            'fetchRequests': False,
            'xmlHttpRequest': False,
            'javaScriptFrameworkSupport': {
                'angular': False,
                'dojo': False,
                'extJS': False,
                'icefaces': False,
                'jQuery': False,
                'mooTools': False,
                'prototype': False,
                'activeXObject': False
            },
            'contentCapture': {
                'resourceTimingSettings': {
                    'w3cResourceTimings': True,
                    'nonW3cResourceTimings': False,
                    'nonW3cResourceTimingsInstrumentationDelay': 50,
                    'resourceTimingCaptureType': None,
                    'resourceTimingsDomainLimit': None
                },
                'javaScriptErrors': True,
                'timeoutSettings': {
                    'timedActionSupport': False,
                    'temporaryActionLimit': 0,
                    'temporaryActionTotalTimeout': 100
                },
                'visuallyCompleteAndSpeedIndex': True,
                'visuallyComplete2Settings': None
            },
            'excludeXhrRegex': '',
            'correlationHeaderInclusionRegex': '',
            'injectionMode': 'JAVASCRIPT_TAG',
            'addCrossOriginAnonymousAttribute': True,
            'scriptTagCacheDurationInHours': 1,
            'libraryFileLocation': '',
            'monitoringDataPath': '',
            'customConfigurationProperties': '',
            'serverRequestPathId': '',
            'secureCookieAttribute': False,
            'cookiePlacementDomain': '',
            'cacheControlHeaderOptimizations': True,
            'advancedJavaScriptTagSettings': {
                'syncBeaconFirefox': False,
                'syncBeaconInternetExplorer': False,
                'instrumentUnsupportedAjaxFrameworks': False,
                'specialCharactersToEscape': '',
                'maxActionNameLength': 100,
                'maxErrorsToCapture': 10,
                'additionalEventHandlers': {
                    'userMouseupEventForClicks': False,
                    'clickEventHandler': False,
                    'mouseupEventHandler': False,
                    'blurEventHandler': False,
                    'changeEventHandler': False,
                    'toStringMethod': False,
                    'maxDomNodesToInstrument': 5000
                },
                'eventWrapperSettings': {
                    'click': False,
                    'mouseUp': False,
                    'change': False,
                    'blur': False,
                    'touchStart': False,
                    'touchEnd': False
                },
                'globalEventCaptureSettings': {
                    'mouseUp': True,
                    'mouseDown': True,
                    'click': True,
                    'doubleClick': True,
                    'keyUp': True,
                    'keyDown': True,
                    'scroll': True,
                    'additionalEventCapturedAsUserInput': ''
                },
                'userActionNameAttribute': None,
                'proxyWrapperEnabled': False
            },
            'browserRestrictionSettings': {
                'mode': 'EXCLUDE',
                'browserRestrictions': []
            },
            'ipAddressRestrictionSettings': {
                'mode': 'EXCLUDE',
                'ipAddressRestrictions': []
            }
        },
        'userActionNamingSettings': {
            'placeholders': [],
            'loadActionNamingRules': [],
            'xhrActionNamingRules': [],
            'customActionNamingRules': [],
            'ignoreCase': True,
            'useFirstDetectedLoadAction': False,
            'splitUserActionsByDomain': True,
            'queryParameterCleanups': [
                'cfid',
                'phpsessid',
                '__sid',
                'cftoken',
                'sid'
            ]
        }
    }

    web_application = copy.deepcopy(web_application_template)
    web_application['name'] = name
    return web_application


def post_application_detection_rule(application_identifier, pattern):
    application_match_target = 'DOMAIN'
    application_match_type = 'MATCHES'
    payload = json.dumps(build_application_detection_rule(application_identifier, application_match_target, application_match_type, pattern))

    endpoint = '/api/config/v1/applicationDetectionRules'

    # delete(endpoint, '4bf59b68-a454-4d9c-9644-8043ca9ac444')
    if offline:
        save('app-detection-rule', application_identifier, payload)
    else:
        post(endpoint, payload)


def build_application_detection_rule(application_identifier, application_match_target, application_match_type, pattern):
    application_detection_rule_template = {
        'applicationIdentifier': 'APPLICATION-032166775CEE7A8C',
        'filterConfig': {
            'pattern': 'foo',
            'applicationMatchType': 'BEGINS_WITH',
            'applicationMatchTarget': 'DOMAIN'
        }
    }
    # applicationMatchTarget: DOMAIN|URL
    # applicationMatchType: BEGINS_WITH|CONTAINS|ENDS_WITH|EQUALS|MATCHES
    # NOTE: MATCHES only works for DOMAIN
    application_detection_rule = copy.deepcopy(application_detection_rule_template)
    application_detection_rule['applicationIdentifier'] = application_identifier
    application_detection_rule['filterConfig']['pattern'] = pattern
    application_detection_rule['filterConfig']['applicationMatchType'] = application_match_type
    application_detection_rule['filterConfig']['applicationMatchTarget'] = application_match_target
    return application_detection_rule


def add_database_relationship_entity_selector_to_tag(tag_id, tag_key, tag_value):
    if offline:
        print('add_database_relationship_entity_selector_to_tag skipped in offline mode...')
        return
    endpoint = '/api/config/v1/autoTags'
    res = get_by_object_id(endpoint, tag_id)
    name = res.get('name')
    if name != tag_key:
        print('Error in "add_database_relationship_entity_selector_to_tag(tag_id, tag_key, tag_value)" method')
        print('Tag name and tag_key do not match!')
        print('Tag ID: ' + tag_id)
        print('Tag Key: ' + tag_key)
        print('Tag Value: ' + tag_value)
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_line_number())
    entity_selector_based_rules = res.get('entitySelectorBasedRules')
    # print(entity_selector_based_rules)
    new_rule = build_database_to_relationship_entity_selector(tag_key, tag_value)
    value_formats = []
    for entity_selector_based_rule in entity_selector_based_rules:
        value_formats.append(entity_selector_based_rule.get('valueFormat'))
    if new_rule.get('valueFormat') in value_formats:
        print('Rule already present...skipping...')
    else:
        entity_selector_based_rules.append(new_rule)
        # print(entity_selector_based_rules)
        res['entitySelectorBasedRules'] = entity_selector_based_rules
        payload = json.dumps(res)
        put(endpoint, tag_id, payload)


def build_database_to_relationship_entity_selector(tag_key, tag_value):
    database_to_relationship_entity_selector_template = {
       'enabled': True,
       'entitySelector': 'type(SERVICE),databaseName.exists(),toRelationships.calls(type(SERVICE),tag(TAG_KEY:TAG_VALUE))',
       'valueFormat': 'TAG_VALUE'
      }
    database_to_relationship_entity_selector = copy.deepcopy(database_to_relationship_entity_selector_template)
    entity_selector = database_to_relationship_entity_selector_template.get('entitySelector')
    entity_selector = entity_selector.replace('TAG_KEY', tag_key)
    entity_selector = entity_selector.replace('TAG_VALUE', tag_value)
    database_to_relationship_entity_selector['entitySelector'] = entity_selector
    database_to_relationship_entity_selector['valueFormat'] = tag_value
    return database_to_relationship_entity_selector


def put_auto_tag(name, attribute, operator, value_format, entity_type):
    object_id = fixed_auto_tag_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_auto_tag_ids dictionary"!')
        exit(get_line_number())

    if auto_tag_prefix != '':
        name = auto_tag_prefix + ' ' + name

    value = None
    condition_comparison_type = 'STRING'
    if attribute == 'HOST_IP_ADDRESS':
        condition_comparison_type = 'IP_ADDRESS'

    condition_comparison_info = {'caseSensitive': None, 'negate': False, 'operator': operator, 'type': condition_comparison_type, 'value': value}
    condition_key = {'attribute': attribute, 'type': 'STATIC'}
    conditions = []
    condition = {'comparisonInfo': condition_comparison_info, 'key': condition_key}
    conditions.append(condition)

    propagation_types = []
    if entity_type == 'HOST':
        propagation_types.append('HOST_TO_PROCESS_GROUP_INSTANCE')
    else:
        if entity_type == 'PROCESS_GROUP':
            propagation_types.extend(['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE'])

    rules = [{'conditions': conditions, 'enabled': True, 'propagationTypes': propagation_types, 'type': entity_type, 'valueFormat': value_format}]

    payload = json.dumps({'name': name, 'rules': rules})

    endpoint = '/api/config/v1/autoTags'

    # delete(endpoint, 'a323b1be-ab6a-31b8-b880-2065fc8f51ec')
    # time.sleep(10)
    if offline:
        save('auto-tag', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_auto_tag_with_propagation_types(name, attribute, operator, value_format, entity_type, propagation_types):
    object_id = fixed_auto_tag_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_auto_tag_ids dictionary"!')
        exit(get_line_number())

    if auto_tag_prefix != '':
        name = auto_tag_prefix + ' ' + name

    value = None
    condition_comparison_type = 'STRING'
    if attribute == 'HOST_IP_ADDRESS':
        condition_comparison_type = 'IP_ADDRESS'

    condition_comparison_info = {'caseSensitive': None, 'negate': False, 'operator': operator, 'type': condition_comparison_type, 'value': value}
    condition_key = {'attribute': attribute, 'type': 'STATIC'}
    conditions = []
    condition = {'comparisonInfo': condition_comparison_info, 'key': condition_key}
    conditions.append(condition)

    rules = [{'conditions': conditions, 'enabled': True, 'propagationTypes': propagation_types, 'type': entity_type, 'valueFormat': value_format}]

    payload = json.dumps({'name': name, 'rules': rules})

    endpoint = '/api/config/v1/autoTags'

    # delete(endpoint, 'a323b1be-ab6a-31b8-b880-2065fc8f51ec')
    # time.sleep(10)
    if offline:
        save('auto-tag', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_auto_tag_typical_process_group_dynamic_key(name, dynamic_key, value_format):
    put_auto_tag_dynamic_key(name, 'PROCESS_GROUP_PREDEFINED_METADATA', dynamic_key, 'PROCESS_PREDEFINED_METADATA_KEY', 'EXISTS', value_format, 'PROCESS_GROUP', ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE'])


def put_auto_tag_dynamic_key(name, attribute, dynamic_key, key_type, operator, value_format, entity_type, propagation_types):
    object_id = fixed_auto_tag_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_auto_tag_ids dictionary"!')
        exit(get_line_number())

    if auto_tag_prefix != '':
        name = auto_tag_prefix + ' ' + name

    condition_comparison_type = 'STRING'
    condition_comparison_info = {'caseSensitive': None, 'negate': False, 'operator': operator, 'type': condition_comparison_type, 'value': None}
    condition_key = {'attribute': attribute, 'dynamicKey': dynamic_key, 'type': key_type}
    conditions = []
    condition = {'comparisonInfo': condition_comparison_info, 'key': condition_key}
    conditions.append(condition)
    rules = [{'conditions': conditions, 'enabled': True, 'propagationTypes': propagation_types, 'type': entity_type, 'valueFormat': value_format}]

    payload = json.dumps({'name': name, 'rules': rules})

    endpoint = '/api/config/v1/autoTags'

    # delete(endpoint, 'a323b1be-ab6a-31b8-b880-2065fc8f51ec')
    # time.sleep(10)
    if offline:
        save('auto-tag', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_auto_tag_os(name, os_list):
    # supported_os_list = ["AIX", "DARWIN", "HPUX", "LINUX", "SOLARIS", "WINDOWS", "ZOS"]

    object_id = fixed_auto_tag_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_auto_tag_ids dictionary"!')
        exit(get_line_number())

    if auto_tag_prefix != '':
        name = auto_tag_prefix + ' ' + name

    rules = []
    key = {'attribute': 'HOST_OS_TYPE', 'type': 'STATIC'}
    propagation_types = ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE']
    for os_type in os_list:
        value = os_type.upper()
        comparison_info = {'negate': False, 'operator': 'EQUALS', 'type': 'OS_TYPE', 'value': value}
        conditions = [{'comparisonInfo': comparison_info, 'key': key}]
        rules.append({'conditions': conditions, 'enabled': True, 'propagationTypes': propagation_types, 'type': 'PROCESS_GROUP', 'valueFormat': os_type})

    payload = json.dumps({'name': name, 'rules': rules})

    endpoint = '/api/config/v1/autoTags'

    if offline:
        save('auto-tag', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_auto_tags_from_host_groups(tag_names, delimiter):
    total_parts = len(tag_names)
    if total_parts < 2:
        print('Error in "put_auto_tags_from_host_groups(tag_names, delimiter)" method')
        print('Two or more host groups parts supported.')
        print('Tag Names: ' + str(tag_names))
        print('Delimiter: ' + delimiter)
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_line_number())

    # five_part_regex = '^[^_]++_[^_]++_[^_]++_[^_]++_[^_]++$'
    # four_part_regex = '^[^_]++_[^_]++_[^_]++_[^_]++_$'
    # three_part_regex = '^[^_]++_[^_]++_[^_]++_$'
    # two_part_regex = '^[^_]++_[^_]++$'

    beginning_regex = '^'
    ending_regex = '$'
    unselected_part_regex = '[^' + delimiter + ']++'
    selected_part_regex = '([^' + delimiter + ']++)'

    tag_name_index = 0
    for tag_name in tag_names:
        object_id = fixed_auto_tag_ids.get(tag_name)

        if not object_id:
            print('No entry for ' + tag_name + ' found in the "fixed_auto_tag_ids dictionary"!')
            exit(get_line_number())

        if auto_tag_prefix != '':
            tag_name = auto_tag_prefix + ' ' + tag_name

        tag_name_index += 1
        rules = []
        extract_regex = beginning_regex
        match_regex = beginning_regex
        for x in range(1, total_parts + 1):
            part_regex = unselected_part_regex
            if x == tag_name_index:
                part_regex = selected_part_regex
            if x < total_parts:
                extract_regex += part_regex + delimiter
                match_regex += unselected_part_regex + delimiter
            else:
                extract_regex += part_regex + ending_regex
                match_regex += unselected_part_regex + ending_regex

        value_format = '{HostGroup:Name/' + extract_regex + '}'
        host_group_extraction_rule = {'conditions': [{'comparisonInfo': {'caseSensitive': True, 'negate': False, 'operator': 'REGEX_MATCHES', 'type': 'STRING', 'value': match_regex}, 'key': {'attribute': 'HOST_GROUP_NAME', 'type': 'STATIC'}}], 'enabled': True, 'propagationTypes': ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE'], 'type': 'PROCESS_GROUP', 'valueFormat': value_format}

        # print(extract_regex)
        # print(match_regex)
        # print(value_format)
        # print(host_group_extraction_rule)

        rules.append(host_group_extraction_rule)

        payload = json.dumps({'name': tag_name, 'rules': rules})

        endpoint = '/api/config/v1/autoTags'

        # delete(endpoint, 'a323b1be-ab6a-31b8-b880-2065fc8f51ec')
        # time.sleep(10)
        if offline:
            save('auto-tag', tag_name, payload)
        else:
            put(endpoint, object_id, payload)


def put_auto_tag_service_topology_type():
    name = 'Service Topology Type'

    object_id = fixed_auto_tag_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_auto_tag_ids dictionary"!')
        exit(get_line_number())

    if auto_tag_prefix != '':
        name = auto_tag_prefix + ' ' + name

    value_settings = [("FULLY_MONITORED", 'Fully Monitored'), ('OPAQUE_SERVICE', 'Opaque'), ('EXTERNAL_SERVICE', 'External')]
    rules = []
    for value_setting in value_settings:
        value = value_setting[0]
        value_format = value_setting[1]
        condition = {'comparisonInfo': {'negate': False, 'operator': 'EQUALS', 'type': 'SERVICE_TOPOLOGY', 'value': value}, 'key': {'attribute': 'SERVICE_TOPOLOGY', 'type': 'STATIC'}}
        rule = {'conditions': [condition], 'enabled': True, 'normalization': 'LEAVE_TEXT_AS_IS', 'propagationTypes': [], 'type': 'SERVICE', 'valueFormat': value_format}
        rules.append(rule)

    payload = json.dumps({'name': name, 'rules': rules})
    endpoint = '/api/config/v1/autoTags'
    # delete(endpoint, 'a323b1be-ab6a-31b8-b880-2065fc8f51ec')
    # time.sleep(10)
    if offline:
        save('auto-tag', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_auto_tag_cloud_provider():
    name = 'Cloud Provider'

    object_id = fixed_auto_tag_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_auto_tag_ids dictionary"!')
        exit(get_line_number())

    if auto_tag_prefix != '':
        name = auto_tag_prefix + ' ' + name

    cloud_providers = ['AWS', 'Azure', 'GCP']

    attribute = ''
    rules = []
    for cloud_provider in cloud_providers:
        value_format = cloud_provider
        enabled = True
        normalization = 'LEAVE_TEXT_AS_IS'
        entity_type = 'PROCESS_GROUP'
        propagation_types = ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE']
        comparison_info_type = 'STRING'
        if cloud_provider == 'AWS':
            attribute = 'AWS_AVAILABILITY_ZONE_NAME'
        else:
            # Azure has two rules, so it's a bit of a mess...
            if cloud_provider == 'Azure':
                attribute = 'AZURE_VM_NAME'
                condition = {'comparisonInfo': {'negate': False, 'operator': 'EXISTS', 'type': 'STRING'}, 'key': {'attribute': attribute, 'type': 'STATIC'}}
                rule = {'conditions': [condition], 'enabled': enabled, 'normalization': normalization, 'propagationTypes': propagation_types, 'type': entity_type, 'valueFormat': value_format}
                rules.append(rule)
                attribute = 'AZURE_ENTITY_NAME'
                entity_type = 'AZURE'
                propagation_types = ['AZURE_TO_PG', 'AZURE_TO_SERVICE']
                comparison_info_type = 'INDEXED_NAME'
            else:
                if cloud_provider == 'GCP':
                    attribute = 'GOOGLE_CLOUD_PLATFORM_ZONE_NAME'

        condition = {'comparisonInfo': {'negate': False, 'operator': 'EXISTS', 'type': comparison_info_type}, 'key': {'attribute': attribute, 'type': 'STATIC'}}
        rule = {'conditions': [condition], 'enabled': True, 'normalization': 'LEAVE_TEXT_AS_IS', 'propagationTypes': propagation_types, 'type': entity_type, 'valueFormat': value_format}
        rules.append(rule)

    payload = json.dumps({'name': name, 'rules': rules})
    endpoint = '/api/config/v1/autoTags'
    # delete(endpoint, 'a323b1be-ab6a-31b8-b880-2065fc8f51ec')
    # time.sleep(10)
    if offline:
        save('auto-tag', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_auto_tag_data_center():
    name = 'Data Center'

    object_id = fixed_auto_tag_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_auto_tag_ids dictionary"!')
        exit(get_line_number())

    if auto_tag_prefix != '':
        name = auto_tag_prefix + ' ' + name

    rules = []
    propagation_types = ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE']
    condition = {'comparisonInfo': {'negate': False, 'operator': 'EXISTS', 'type': 'STRING'}, 'key': {'attribute': 'AWS_AVAILABILITY_ZONE_NAME', 'type': 'STATIC'}}
    rule = {'conditions': [condition], 'enabled': True, 'normalization': 'LEAVE_TEXT_AS_IS', 'propagationTypes': propagation_types, 'type': 'PROCESS_GROUP', 'valueFormat': '{AwsAvailabilityZone:Name} (Source: AWS AZ)'}
    rules.append(rule)
    condition = {'comparisonInfo': {'negate': False, 'operator': 'EXISTS', 'type': 'STRING'}, 'key': {'attribute': 'VMWARE_DATACENTER_NAME', 'type': 'STATIC'}}
    rule = {'conditions': [condition], 'enabled': True, 'normalization': 'LEAVE_TEXT_AS_IS', 'propagationTypes': propagation_types, 'type': 'PROCESS_GROUP', 'valueFormat': '{VmwareDatacenter:Name} (Source: VMWare DC)'}
    rules.append(rule)

    for location_tuple in [
        ('Ashburn', 'Ashburn, VA'),
        ('Burlington', 'Burlington, NC'),
        ('Charlotte', 'Charlotte, NC'),
        ('DFW', 'DFW'),
        ('DUB', 'Dublin'),
        ('Durham', 'Durham, NC'),
        ('EDC', 'EDC'),
        ('Indianapolis', 'Indianapolis, IN'),
        ('Mebane', 'Mebane, NC'),
        ('Mt. Pleasant', 'Mt. Pleasant, SC'),
        ('Poynette', 'Poynette, WI'),
        ('Research Triangle Park', 'RTP'),
        ('Richmond', 'Richmond, VA'),
        ('SGP', 'Singapore'),
    ]:
        conditions = []
        condition = {
            'comparisonInfo': {'negate': False, 'operator': 'BEGINS_WITH', 'value': location_tuple[0] + ';', 'type': 'STRING', 'caseSensitive': True}, 'key': {'attribute': 'OPENSTACK_REGION_NAME', 'type': 'STATIC'}}
        conditions.append(condition)
        condition = {'comparisonInfo': {'negate': True, 'operator': 'EXISTS', 'type': 'STRING'}, 'key': {'attribute': 'AWS_AVAILABILITY_ZONE_NAME', 'type': 'STATIC'}}
        conditions.append(condition)
        condition = {'comparisonInfo': {'negate': True, 'operator': 'EXISTS', 'type': 'STRING'}, 'key': {'attribute': 'VMWARE_DATACENTER_NAME', 'type': 'STATIC'}}
        conditions.append(condition)
        rule = {'conditions': conditions, 'enabled': True, 'normalization': 'LEAVE_TEXT_AS_IS', 'propagationTypes': propagation_types, 'type': 'PROCESS_GROUP', 'valueFormat': location_tuple[1] + ' (Source: IP Geolocation)'}
        rules.append(rule)

    payload = json.dumps({'name': name, 'rules': rules})
    endpoint = '/api/config/v1/autoTags'
    if offline:
        save('auto-tag', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_auto_tag_process_technology():
    name = 'Technology'

    object_id = fixed_auto_tag_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_auto_tag_ids dictionary"!')
        exit(get_line_number())

    if auto_tag_prefix != '':
        name = auto_tag_prefix + ' ' + name

    # From config spec
    # full_technology_list = ["ACTIVE_MQ", "ACTIVE_MQ_ARTEMIS", "ADO_NET", "AIX", "AKKA", "AMAZON_REDSHIFT", "AMQP", "APACHE_CAMEL", "APACHE_CASSANDRA", "APACHE_COUCH_DB", "APACHE_DERBY", "APACHE_HTTP_CLIENT_ASYNC", "APACHE_HTTP_CLIENT_SYNC", "APACHE_HTTP_SERVER", "APACHE_KAFKA", "APACHE_LOG4J", "APACHE_SOLR", "APACHE_STORM", "APACHE_SYNAPSE", "APACHE_TOMCAT", "APPARMOR", "APPLICATION_INSIGHTS_SDK", "ASP_DOTNET", "ASP_DOTNET_CORE", "ASP_DOTNET_CORE_SIGNALR", "ASP_DOTNET_SIGNALR", "ASYNC_HTTP_CLIENT", "AWS_LAMBDA", "AWS_RDS", "AWS_SERVICE", "AXIS", "AZURE_FUNCTIONS", "AZURE_SERVICE_BUS", "AZURE_SERVICE_FABRIC", "AZURE_STORAGE", "BOSHBPM", "CITRIX", "CITRIX_COMMON", "CITRIX_DESKTOP_DELIVERY_CONTROLLERS", "CITRIX_DIRECTOR", "CITRIX_LICENSE_SERVER", "CITRIX_PROVISIONING_SERVICES", "CITRIX_STOREFRONT", "CITRIX_VIRTUAL_DELIVERY_AGENT", "CITRIX_WORKSPACE_ENVIRONMENT_MANAGEMENT", "CITRIX_XEN", "CLOUDFOUNDRY", "CLOUDFOUNDRY_AUCTIONEER", "CLOUDFOUNDRY_BOSH", "CLOUDFOUNDRY_GOROUTER", "COLDFUSION", "CONFLUENT_KAFKA_CLIENT", "CONTAINERD", "CORE_DNS", "COUCHBASE", "CRIO", "CXF", "DATASTAX", "DB2", "DIEGO_CELL", "DOCKER", "DOTNET", "DOTNET_REMOTING", "ELASTIC_SEARCH", "ENVOY", "ERLANG", "ETCD", "F5_LTM", "FSHARP", "GARDEN", "GLASSFISH", "GO", "GOOGLE_CLOUD_FUNCTIONS", "GRAAL_TRUFFLE", "GRPC", "GRSECURITY", "HADOOP", "HADOOP_HDFS", "HADOOP_YARN", "HAPROXY", "HEAT", "HESSIAN", "HORNET_Q", "IBM_CICS_REGION", "IBM_CICS_TRANSACTION_GATEWAY", "IBM_IMS_CONNECT_REGION", "IBM_IMS_CONTROL_REGION", "IBM_IMS_MESSAGE_PROCESSING_REGION", "IBM_IMS_SOAP_GATEWAY", "IBM_INTEGRATION_BUS", "IBM_MQ", "IBM_MQ_CLIENT", "IBM_WEBSHPRERE_APPLICATION_SERVER", "IBM_WEBSHPRERE_LIBERTY", "IBM_WEBSPHERE_APPLICATION_SERVER", "IBM_WEBSPHERE_LIBERTY", "IIS", "IIS_APP_POOL", "ISTIO", "JAVA", "JAX_WS", "JBOSS", "JBOSS_EAP", "JDK_HTTP_SERVER", "JERSEY", "JETTY", "JRUBY", "JYTHON", "KUBERNETES", "LIBC", "LIBVIRT", "LINKERD", "LINUX_SYSTEM", "MARIADB", "MEMCACHED", "MICROSOFT_SQL_SERVER", "MONGODB", "MSSQL_CLIENT", "MULE_ESB", "MYSQL", "MYSQL_CONNECTOR", "NETFLIX_SERVO", "NETTY", "NGINX", "NODE_JS", "OK_HTTP_CLIENT", "ONEAGENT_SDK", "OPENCENSUS", "OPENSHIFT", "OPENSTACK_COMPUTE", "OPENSTACK_CONTROLLER", "OPENTELEMETRY", "OPENTRACING", "OPEN_LIBERTY", "ORACLE_DATABASE", "ORACLE_WEBLOGIC", "OWIN", "PERL", "PHP", "PHP_FPM", "PLAY", "POSTGRE_SQL", "POSTGRE_SQL_DOTNET_DATA_PROVIDER", "POWER_DNS", "PROGRESS", "PYTHON", "QOS_LOGBACK", "RABBIT_MQ", "REACTOR_CORE", "REDIS", "RESTEASY", "RESTLET", "RIAK", "RUBY", "RUNC", "RXJAVA", "SAG_WEBMETHODS_IS", "SAP", "SAP_HANADB", "SAP_HYBRIS", "SAP_MAXDB", "SAP_SYBASE", "SCALA", "SELINUX", "SHAREPOINT", "SPARK", "SPRING", "SQLITE", "THRIFT", "TIBCO", "TIBCO_BUSINESS_WORKS", "TIBCO_EMS", "UNDERTOW_IO", "VARNISH_CACHE", "VERTX", "VIM2", "VIOS", "VIRTUAL_MACHINE_KVM", "VIRTUAL_MACHINE_QEMU", "WILDFLY", "WINDOWS_CONTAINERS", "WINDOWS_SYSTEM", "WINK", "ZERO_MQ", "ZOS_CONNECT" ]

    technology_list = ["ADO_NET", "AIX", "APACHE_CASSANDRA", "APACHE_COUCH_DB", "APACHE_DERBY", "APACHE_HTTP_CLIENT_ASYNC", "APACHE_HTTP_CLIENT_SYNC", "APACHE_HTTP_SERVER", "APACHE_KAFKA", "APACHE_LOG4J", "APACHE_SOLR", "APACHE_STORM", "APACHE_SYNAPSE", "APACHE_TOMCAT", "ASP_DOTNET", "ASP_DOTNET_CORE", "ASP_DOTNET_CORE_SIGNALR", "ASP_DOTNET_SIGNALR", "CONFLUENT_KAFKA_CLIENT", "COUCHBASE", "DB2", "DOTNET", "DOTNET_REMOTING", "ELASTIC_SEARCH", "ENVOY", "ERLANG", "ETCD", "GO", "HAPROXY", "IBM_MQ", "IBM_MQ_CLIENT", "IBM_WEBSPHERE_APPLICATION_SERVER", "IBM_WEBSPHERE_LIBERTY", "IIS", "IIS_APP_POOL", "JAVA", "JBOSS", "JBOSS_EAP", "JETTY", "KUBERNETES", "LINUX_SYSTEM", "MARIADB", "MEMCACHED", "MICROSOFT_SQL_SERVER", "MONGODB", "MSSQL_CLIENT", "MULE_ESB", "MYSQL", "MYSQL_CONNECTOR", "NETTY", "NGINX", "NODE_JS", "OPENSHIFT", "OPENSTACK_COMPUTE", "OPENSTACK_CONTROLLER", "ORACLE_DATABASE", "ORACLE_WEBLOGIC", "OWIN", "PERL", "PHP", "PHP_FPM", "PLAY", "POSTGRE_SQL", "PROGRESS", "PYTHON", "RABBIT_MQ", "REDIS", "RUBY", "SPRING", "TIBCO", "TIBCO_BUSINESS_WORKS", "TIBCO_EMS", "VARNISH_CACHE", "WINDOWS_SYSTEM"]
    rules = []
    for technology in technology_list:
        condition_comparison_info = {'caseSensitive': None, 'negate': False, 'operator': 'EQUALS', 'type': 'SIMPLE_TECH', 'value': {'type': technology}}
        condition_key = {'attribute': 'PROCESS_GROUP_TECHNOLOGY', 'type': 'STATIC'}
        conditions = []
        condition = {'comparisonInfo': condition_comparison_info, 'key': condition_key}
        conditions.append(condition)
        propagation_types = ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE']
        rules.append({'conditions': conditions, 'enabled': True, 'propagationTypes': propagation_types, 'type': 'PROCESS_GROUP', 'valueFormat': technology})
    payload = json.dumps({'name': name, 'rules': rules})
    endpoint = '/api/config/v1/autoTags'
    if offline:
        save('auto-tag', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_auto_tag_host_technology():
    name = 'Host Technology'

    object_id = fixed_auto_tag_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_auto_tag_ids dictionary"!')
        exit(get_line_number())

    if auto_tag_prefix != '':
        name = auto_tag_prefix + ' ' + name

    # From config spec
    # full_technology_list = [ "APPARMOR", "BOSH", "BOSHBPM", "CLOUDFOUNDRY", "CONTAINERD", "CRIO", "DIEGO_CELL", "DOCKER", "GARDEN", "GRSECURITY", "KUBERNETES", "OPENSHIFT", "OPENSTACK_COMPUTE", "OPENSTACK_CONTROLLER", "SELINUX" ]

    technology_list = ["APPARMOR", "BOSH", "BOSHBPM", "CLOUDFOUNDRY", "CONTAINERD", "CRIO", "DIEGO_CELL", "DOCKER", "GARDEN", "GRSECURITY", "KUBERNETES", "OPENSHIFT", "OPENSTACK_COMPUTE", "OPENSTACK_CONTROLLER", "SELINUX"]
    rules = []
    for technology in technology_list:
        condition_comparison_info = {'caseSensitive': None, 'negate': False, 'operator': 'EQUALS', 'type': 'SIMPLE_HOST_TECH', 'value': {'type': technology}}
        condition_key = {'attribute': 'HOST_TECHNOLOGY', 'type': 'STATIC'}
        conditions = []
        condition = {'comparisonInfo': condition_comparison_info, 'key': condition_key}
        conditions.append(condition)
        propagation_types = ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE']
        rules.append({'conditions': conditions, 'enabled': True, 'propagationTypes': propagation_types, 'type': 'PROCESS_GROUP', 'valueFormat': technology})
    payload = json.dumps({'name': name, 'rules': rules})
    endpoint = '/api/config/v1/autoTags'
    # delete(endpoint, 'a323b1be-ab6a-31b8-b880-2065fc8f51ec')
    # time.sleep(10)
    if offline:
        save('auto-tag', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_auto_tag_host_group():
    name = 'Host Group'

    object_id = fixed_auto_tag_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_auto_tag_ids dictionary"!')
        exit(get_line_number())

    if auto_tag_prefix != '':
        name = auto_tag_prefix + ' ' + name

    rules = []
    # Host Group Exists
    conditions = []
    condition_comparison_info = {'caseSensitive': None, 'negate': False, 'operator': 'EXISTS', 'type': 'STRING', 'value': None}
    condition_key = {'attribute': 'HOST_GROUP_NAME', 'type': 'STATIC'}
    condition = {'comparisonInfo': condition_comparison_info, 'key': condition_key}
    conditions.append(condition)
    rules.append({'conditions': conditions, 'enabled': True, 'propagationTypes': ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE'], 'type': 'PROCESS_GROUP', 'valueFormat': '{HostGroup:Name}'})
    # Host Group Does Not Exist and Not Kubernetes
    conditions = []
    condition_comparison_info = {'caseSensitive': None, 'negate': True, 'operator': 'EXISTS', 'type': 'STRING', 'value': None}
    condition_key = {'attribute': 'HOST_GROUP_NAME', 'type': 'STATIC'}
    condition = {'comparisonInfo': condition_comparison_info, 'key': condition_key}
    conditions.append(condition)
    condition_comparison_info = {'caseSensitive': None, 'negate': True, 'operator': 'EXISTS', 'type': 'STRING', 'value': None}
    condition_key = {'attribute': 'KUBERNETES_CLUSTER_NAME', 'type': 'STATIC'}
    condition = {'comparisonInfo': condition_comparison_info, 'key': condition_key}
    conditions.append(condition)
    rules.append({'conditions': conditions, 'enabled': True, 'propagationTypes': ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE'], 'type': 'PROCESS_GROUP', 'valueFormat': '.None'})
    # Host Group Does Not Exist and Kubernetes
    conditions = []
    condition_comparison_info = {'caseSensitive': None, 'negate': True, 'operator': 'EXISTS', 'type': 'STRING', 'value': None}
    condition_key = {'attribute': 'HOST_GROUP_NAME', 'type': 'STATIC'}
    condition = {'comparisonInfo': condition_comparison_info, 'key': condition_key}
    conditions.append(condition)
    condition_comparison_info = {'caseSensitive': None, 'negate': False, 'operator': 'EXISTS', 'type': 'STRING', 'value': None}
    condition_key = {'attribute': 'KUBERNETES_CLUSTER_NAME', 'type': 'STATIC'}
    condition = {'comparisonInfo': condition_comparison_info, 'key': condition_key}
    conditions.append(condition)
    rules.append({'conditions': conditions, 'enabled': True, 'propagationTypes': ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE'], 'type': 'PROCESS_GROUP', 'valueFormat': '.None (OCP/K8s)'})
    # put_auto_tag('Kubernetes Cluster', 'KUBERNETES_CLUSTER_NAME', 'EXISTS', '{KubernetesCluster:Name}', 'PROCESS_GROUP')
    payload = json.dumps({'name': name, 'rules': rules})
    endpoint = '/api/config/v1/autoTags'
    if offline:
        save('auto-tag', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_auto_tag_aws_region():
    name = 'AWS Region'

    object_id = fixed_auto_tag_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_auto_tag_ids dictionary"!')
        exit(get_line_number())

    if auto_tag_prefix != '':
        name = auto_tag_prefix + ' ' + name

    rules = []

    condition_key = {'attribute': 'AWS_AVAILABILITY_ZONE_NAME', 'type': 'STATIC'}

    for region_tuple in [('us-east-2', 'US East (Ohio)'), ('us-east-1', 'US East (N. Virginia)'), ('us-west-1', 'US West (N. California)'), ('us-west-2', 'US West (Oregon)'), ('af-south-1', 'Africa (Cape Town)'), ('ap-east-1', 'Asia Pacific (Hong Kong)'), ('ap-southeast-3', 'Asia Pacific (Jakarta)'), ('ap-south-1', 'Asia Pacific (Mumbai)'), ('ap-northeast-3', 'Asia Pacific (Osaka)'), ('ap-northeast-2', 'Asia Pacific (Seoul)'), ('ap-southeast-1', 'Asia Pacific (Singapore)'), ('ap-southeast-2', 'Asia Pacific (Sydney)'), ('ap-northeast-1', 'Asia Pacific (Tokyo)'), ('ca-central-1', 'Canada (Central)'), ('eu-central-1', 'Europe (Frankfurt)'), ('eu-west-1', 'Europe (Ireland)'), ('eu-west-2', 'Europe (London)'), ('eu-south-1', 'Europe (Milan)'), ('eu-west-3', 'Europe (Paris)'), ('eu-north-1', 'Europe (Stockholm)'), ('me-south-1', 'Middle East (Bahrain)'), ('me-central-1', 'Middle East (UAE)'), ('sa-east-1', 'South America (São Paulo)')]:
        condition_comparison_info = {'caseSensitive': False, 'negate': False, 'operator': 'BEGINS_WITH', 'type': 'STRING', 'value': region_tuple[0]}
        condition = {'comparisonInfo': condition_comparison_info, 'key': condition_key}
        conditions = [condition]
        rules.append({'conditions': conditions, 'enabled': True, 'propagationTypes': ['PROCESS_GROUP_TO_HOST', 'PROCESS_GROUP_TO_SERVICE'], 'type': 'PROCESS_GROUP', 'valueFormat': region_tuple[0] + ' - ' + region_tuple[1]})

    '''
    From https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions
    us-east-2 -	US East (Ohio)
    us-east-1 -	US East (N. Virginia)
    us-west-1 - US West (N. California)
    us-west-2 - US West (Oregon)
    af-south-1 - Africa (Cape Town)
    ap-east-1 - Asia Pacific (Hong Kong)
    ap-southeast-3 - Asia Pacific (Jakarta)
    ap-south-1 - Asia Pacific (Mumbai)
    ap-northeast-3 - Asia Pacific (Osaka)
    ap-northeast-2 - Asia Pacific (Seoul)
    ap-southeast-1 - Asia Pacific (Singapore)
    ap-southeast-2 - Asia Pacific (Sydney)
    ap-northeast-1 - Asia Pacific (Tokyo)
    ca-central-1 - Canada (Central)
    eu-central-1 - Europe (Frankfurt)
    eu-west-1 - Europe (Ireland)
    eu-west-2 - Europe (London)
    eu-south-1 - Europe (Milan)
    eu-west-3 - Europe (Paris)
    eu-north-1 - Europe (Stockholm)
    me-south-1 - Middle East (Bahrain)
    me-central-1 - Middle East (UAE)
    sa-east-1 - South America (São Paulo)
    '''

    payload = json.dumps({'name': name, 'rules': rules})
    endpoint = '/api/config/v1/autoTags'
    if offline:
        save('auto-tag', name, payload)
    else:
        put(endpoint, object_id, payload)


def save(path, name, payload):
    # TODO: Create directory if it doesn't already exist
    json_data = json.dumps(json.loads(payload), indent=4, sort_keys=False)
    filename = path + '/' + name.replace(' ', '_').replace(':', '_') + '.json'
    with open(filename, 'w') as file:
        file.write(json_data)


def dump_json(endpoint, object_id):
    response = get_by_object_id(endpoint, object_id)
    json_data = json.dumps(response, indent=4, sort_keys=False)
    print(json_data)
    with open('$DUMP-' + object_id, 'w') as file:
        file.write(json_data)


def get_by_object_id(endpoint, object_id):
    return dynatrace_api.get_by_object_id(env, token, endpoint, object_id)


def get_object_list(endpoint: str) -> Response:
    return dynatrace_api.get_object_list(env, token, endpoint)


def put_conditional_naming_rules(rule_type, name, attribute, name_format):
    object_id = fixed_conditional_naming_rules_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_conditional_naming_rules_ids dictionary"!')
        exit(get_line_number())

    comparison_info = {'operator': 'EXISTS', 'type': 'STRING', 'negate': False}
    key = {'attribute': attribute, 'type': 'STATIC'}
    rules = [{'comparisonInfo': comparison_info, 'key': key}]
    if rule_type == 'processGroup':
        entity_type = 'PROCESS_GROUP'
    else:
        entity_type = rule_type.upper()

    payload = json.dumps({'displayName': name, 'enabled': False, 'nameFormat': name_format, 'type': entity_type, 'rules': rules})
    endpoint = '/api/config/v1/conditionalNaming/' + rule_type
    # delete(endpoint, 'a323b1be-ab6a-31b8-b880-2065fc8f51ec')
    # time.sleep(10)
    if offline:
        save('conditional-naming-' + rule_type.lower(), name, payload)
    else:
        put(endpoint, object_id, payload)


def put_conditional_naming_rules_non_k8s(rule_type, name, attribute, name_format):
    object_id = fixed_conditional_naming_rules_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_conditional_naming_rules_ids dictionary"!')
        exit(get_line_number())

    comparison_info = {'operator': 'EXISTS', 'type': 'STRING', 'negate': False}
    comparison_info_non_k8s = {'operator': 'EXISTS', 'type': 'STRING', 'negate': True}
    key = {'attribute': attribute, 'type': 'STATIC'}
    key_non_k8s = {'attribute': 'PROCESS_GROUP_PREDEFINED_METADATA', 'dynamicKey': 'KUBERNETES_NAMESPACE', 'type': 'PROCESS_PREDEFINED_METADATA_KEY'}
    rules = [{'comparisonInfo': comparison_info, 'key': key}, {'comparisonInfo': comparison_info_non_k8s, 'key': key_non_k8s}]
    if rule_type == 'processGroup':
        entity_type = 'PROCESS_GROUP'
    else:
        entity_type = rule_type.upper()

    payload = json.dumps({'displayName': name, 'enabled': False, 'nameFormat': name_format, 'type': entity_type, 'rules': rules})
    endpoint = '/api/config/v1/conditionalNaming/' + rule_type
    # delete(endpoint, 'a323b1be-ab6a-31b8-b880-2065fc8f51ec')
    # time.sleep(10)
    if offline:
        save('conditional-naming-' + rule_type.lower(), name, payload)
    else:
        put(endpoint, object_id, payload)


def put_conditional_naming_rules_k8s(rule_type, name, name_format):
    object_id = fixed_conditional_naming_rules_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_conditional_naming_rules_ids dictionary"!')
        exit(get_line_number())

    comparison_info_k8s = {'operator': 'EXISTS', 'type': 'STRING', 'negate': False}
    key_k8s = {'attribute': 'PROCESS_GROUP_PREDEFINED_METADATA', 'dynamicKey': 'KUBERNETES_NAMESPACE', 'type': 'PROCESS_PREDEFINED_METADATA_KEY'}
    rules = [{'comparisonInfo': comparison_info_k8s, 'key': key_k8s}]
    if rule_type == 'processGroup':
        entity_type = 'PROCESS_GROUP'
    else:
        entity_type = rule_type.upper()

    payload = json.dumps({'displayName': name, 'enabled': False, 'nameFormat': name_format, 'type': entity_type, 'rules': rules})
    endpoint = '/api/config/v1/conditionalNaming/' + rule_type
    # delete(endpoint, 'a323b1be-ab6a-31b8-b880-2065fc8f51ec')
    # time.sleep(10)
    if offline:
        save('conditional-naming-' + rule_type.lower(), name, payload)
    else:
        put(endpoint, object_id, payload)


def put_request_attribute(name, source, parameter):
    object_id = fixed_request_attribute_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_request_attribute_ids dictionary"!')
        exit(get_line_number())

    capturing_and_storage_location = 'CAPTURE_AND_STORE_ON_SERVER'
    if name == 'x-dynatrace (client-side)':
        capturing_and_storage_location = 'CAPTURE_AND_STORE_ON_CLIENT'

    if parameter:
        data_sources = [{"enabled": True, "source": source, "parameterName": parameter, "capturingAndStorageLocation": capturing_and_storage_location, "valueProcessing": {"splitAt": "", "trim": False}}]
    else:
        data_sources = [{"enabled": True, "source": source, "valueProcessing": {"splitAt": "", "trim": False}}]

    if source == 'CLIENT_IP' or source == 'REQUEST_HEADER':
        skip_personal_data_masking = True
    else:
        skip_personal_data_masking = False

    payload = json.dumps({'id': object_id, 'name': name, "dataType": "STRING", "dataSources": data_sources, "aggregation": "FIRST", "normalization": "ORIGINAL", "enabled": True, "confidential": False, "skipPersonalDataMasking": skip_personal_data_masking})
    endpoint = '/api/config/v1/service/requestAttributes'
    if offline:
        save('request-attributes', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_request_attribute_with_value_processing_control(name, source, parameter, value_processing):
    object_id = fixed_request_attribute_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_request_attribute_ids dictionary"!')
        exit(get_line_number())

    if parameter:
        data_sources = [{"enabled": True, "source": source, "parameterName": parameter, "capturingAndStorageLocation": "CAPTURE_AND_STORE_ON_SERVER", "valueProcessing": value_processing}]
    else:
        data_sources = [{"enabled": True, "source": source, "valueProcessing": value_processing}]

    payload = json.dumps({'name': name, "dataType": "STRING", "dataSources": data_sources, "aggregation": "FIRST", "normalization": "ORIGINAL", "enabled": True, "confidential": False, "skipPersonalDataMasking": False})
    endpoint = '/api/config/v1/service/requestAttributes'
    if offline:
        save('request-attributes', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_request_attribute_tenable_client_ip():
    name = 'Tenable Client IP'

    tenable_client_ip_list = environment.get_configuration('robot_admin_enable_client_ip_list')

    if not tenable_client_ip_list:
        print('The Tenable Client IP List is empty.  Nothing to do!')
        return

    object_id = fixed_request_attribute_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_request_attribute_ids dictionary"!')
        exit(get_line_number())

    data_sources = []
    for tenable_client_ip in tenable_client_ip_list:
        value_processing = {'splitAt': '', 'trim': False, 'valueCondition': {'negate': False, 'operator': 'EQUALS', 'value': tenable_client_ip}}
        data_sources.append({"enabled": True, "source": 'CLIENT_IP', "valueProcessing": value_processing})

    payload = json.dumps({'id': object_id, 'name': name, "dataType": "STRING", "dataSources": data_sources, "aggregation": "FIRST", "normalization": "ORIGINAL", "enabled": True, "confidential": False, "skipPersonalDataMasking": True})
    endpoint = '/api/config/v1/service/requestAttributes'
    if offline:
        save('request-attributes', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_request_attribute_load_testing(name, source, parameter, delimiter, end_delimiter, position):
    object_id = fixed_request_attribute_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_request_attribute_ids dictionary"!')
        exit(get_line_number())

    extract_substring = {"delimiter": delimiter, "endDelimiter": end_delimiter, "position": position}
    value_processing = {"extractSubstring": extract_substring, "splitAt": "", "trim": False}
    data_sources = [{"enabled": True, "source": source, "parameterName": parameter, "valueProcessing": value_processing, "capturingAndStorageLocation": 'CAPTURE_AND_STORE_ON_SERVER'}]

    payload = json.dumps({'name': name, "dataType": "STRING", "dataSources": data_sources, "aggregation": "FIRST", "normalization": "ORIGINAL", "enabled": True, "confidential": False, "skipPersonalDataMasking": False})
    endpoint = '/api/config/v1/service/requestAttributes'
    if offline:
        save('request-attributes', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_request_attribute_request_id():
    name = 'RequestId'

    object_id = fixed_request_attribute_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_request_attribute_ids dictionary"!')
        exit(get_line_number())

    template = {
     "aggregation": "FIRST",
     "confidential": False,
     "dataSources": [
      {
       "enabled": True,
       "methods": [
        {
         "argumentIndex": 0,
         "capture": "ARGUMENT",
         "method": {
          "argumentTypes": [
           "javax.servlet.http.HttpServletRequest"
          ],
          "className": "ca.uhn.fhir.rest.server.RestfulServer",
          "methodName": "getOrCreateRequestId",
          "modifiers": [],
          "returnType": "java.lang.String",
          "visibility": "PROTECTED"
         }
        }
       ],
       "source": "METHOD_PARAM",
       "technology": "JAVA",
       "valueProcessing": {
        "splitAt": "",
        "trim": False
       }
      }
     ],
     "dataType": "STRING",
     "enabled": True,
     "name": name,
     "normalization": "ORIGINAL",
     "skipPersonalDataMasking": True
    }

    payload = json.dumps(template)
    endpoint = '/api/config/v1/service/requestAttributes'
    if offline:
        save('request-attributes', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_tenable_request_naming_rules():
    name = 'Tenable Request'

    object_id = fixed_request_naming_rules_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_request_naming_rules_ids dictionary"!')
        exit(get_line_number())

    conditions = [{"attribute": "SERVICE_REQUEST_ATTRIBUTE", "comparisonInfo": {"caseSensitive": False, "comparison": "EXISTS", "matchOnChildCalls": False, "negate": False, "requestAttribute": "Tenable Client IP", "source": None, "type": "STRING_REQUEST_ATTRIBUTE", "value": None, "values": None}}]
    payload = json.dumps({"conditions": conditions, "enabled": True, "namingPattern": name, "placeholders": []})
    endpoint = '/api/config/v1/service/requestNaming'
    if offline:
        save('request-naming-service', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_health_check_request_naming_rules_user_agent():
    name = 'Health Check Request (User Agent)'

    object_id = fixed_request_naming_rules_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_request_naming_rules_ids dictionary"!')
        exit(get_line_number())

    template = {
     "conditions": [
      {
       "attribute": "SERVICE_REQUEST_ATTRIBUTE",
       "comparisonInfo": {
        "caseSensitive": False,
        "comparison": "REGEX_MATCHES",
        "matchOnChildCalls": False,
        "negate": False,
        "requestAttribute": "User Agent Type",
        "source": None,
        "type": "STRING_REQUEST_ATTRIBUTE",
        "value": "ELB-HealthChecker|kube-probe|curl",
        "values": None
       }
      }
     ],
     "enabled": True,
     "namingPattern": "Health Check Request",
     "placeholders": []
    }
    payload = json.dumps(template)
    endpoint = '/api/config/v1/service/requestNaming'
    if offline:
        save('request-naming-service', name, payload)
    else:
        put(endpoint, object_id, payload)


def put_health_check_request_naming_rules_urls():
    name = 'Health Check Request (URLs)'

    object_id = fixed_request_naming_rules_ids.get(name)

    if not object_id:
        print('No entry for ' + name + ' found in the "fixed_request_naming_rules_ids dictionary"!')
        exit(get_line_number())

    template = {
     "conditions": [
      {
       "attribute": "WEBREQUEST_URL_PATH",
       "comparisonInfo": {
        "caseSensitive": False,
        "comparison": "REGEX_MATCHES",
        "negate": False,
        "type": "STRING",
        # "value": "/f5/monitor|/keepalive.htm|/webtest.html|/test.htm$|/webTest$|/health$|/healthCheck$|ping$",
        "value": "/healthCheck|/health$|/ready$|/readyz$|/heartbeat|/keepalive",
        "values": None
       }
      }
     ],
     "enabled": True,
     "namingPattern": "Health Check Request",
     "placeholders": []
    }

    payload = json.dumps(template)
    endpoint = '/api/config/v1/service/requestNaming'
    if offline:
        save('request-naming-service', name, payload)
    else:
        put(endpoint, object_id, payload)


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def delete_all_entities_with_fixed_ids():
    delete_auto_tags_with_fixed_ids()
    delete_request_attributes_with_fixed_ids()
    delete_request_naming_rules_with_fixed_ids()
    delete_conditional_naming_rules_with_fixed_ids()


def delete_auto_tags_with_fixed_ids():
    # Safety Check
    if env_name not in ['Personal', 'Demo']:
        print('Error in "delete_auto_tags_with_fixed_ids()" method')
        print('Not for use in this environment')
        print('Env: ' + env)
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_line_number())

    endpoint = '/api/config/v1/autoTags'
    r = get_object_list(endpoint)
    auto_tags_json = json.loads(r.text)
    auto_tag_list = auto_tags_json.get('values')
    for auto_tag in auto_tag_list:
        object_id = auto_tag.get('id')
        name = auto_tag.get('name')
        if auto_tag_prefix != '':
            original_name = name.replace(auto_tag_prefix + ' ', '')
        else:
            original_name = name
        if object_id == fixed_auto_tag_ids.get(original_name):
            print('Deleting ' + name + ' (' + original_name + '): ', object_id)
            delete(endpoint, object_id)


def delete_request_attributes_with_fixed_ids():
    # Safety Check
    if env_name not in ['Personal', 'Demo']:
        print('Error in "delete_request_attributes_with_fixed_ids()" method')
        print('Not for use in this environment')
        print('Env: ' + env)
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_line_number())

    endpoint = '/api/config/v1/service/requestAttributes'
    r = get_object_list(endpoint)
    request_attributes_json = json.loads(r.text)
    request_attribute_list = request_attributes_json.get('values')
    for request_attribute in request_attribute_list:
        object_id = request_attribute.get('id')
        name = request_attribute.get('name')
        if object_id == fixed_request_attribute_ids.get(name):
            print('Deleting', name, object_id)
            delete(endpoint, object_id)


def delete_request_naming_rules_with_fixed_ids():
    # Safety Check
    if env_name not in ['Personal', 'Demo']:
        print('Error in "delete_request_naming_rules_with_fixed_ids()" method')
        print('Not for use in this environment')
        print('Env: ' + env)
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_line_number())

    endpoint = '/api/config/v1/service/requestNaming'
    r = get_object_list(endpoint)
    request_naming_rules_json = json.loads(r.text)
    request_naming_rule_list = request_naming_rules_json.get('values')
    for request_naming_rule in request_naming_rule_list:
        object_id = request_naming_rule.get('id')
        name = request_naming_rule.get('name')
        # print(object_id, name)
        # Need to be looser here since names are not carried as is to rules, just go by ID.
        if object_id in str(fixed_request_naming_rules_ids):
            print('Deleting', name, object_id)
            delete(endpoint, object_id)


def delete_conditional_naming_rules_with_fixed_ids():
    # Safety Check
    if env_name not in ['Personal', 'Demo']:
        print('Error in "delete_conditional_naming_rules_with_fixed_ids()" method')
        print('Not for use in this environment')
        print('Env: ' + env)
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_line_number())

    for rule_type in ['host', 'processGroup', 'service']:
        endpoint = '/api/config/v1/conditionalNaming/' + rule_type
        r = get_object_list(endpoint)
        conditional_naming_rules_json = json.loads(r.text)
        conditional_naming_rule_list = conditional_naming_rules_json.get('values')
        for conditional_naming_rule in conditional_naming_rule_list:
            object_id = conditional_naming_rule.get('id')
            name = conditional_naming_rule.get('name')
            if object_id == fixed_conditional_naming_rules_ids.get(name):
                print('Deleting ', name, object_id)
                delete(endpoint, object_id)


def delete_auto_tags():
    # Safety Check
    if env_name not in ['Personal', 'Demo']:
        print('Error in "delete_auto_tags()" method')
        print('Not for use in this environment')
        print('Env: ' + env)
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_line_number())

    endpoint = '/api/config/v1/autoTags'
    r = get_object_list(endpoint)
    auto_tags_json = json.loads(r.text)
    auto_tag_list = auto_tags_json.get('values')
    for auto_tag in auto_tag_list:
        object_id = auto_tag.get('id')
        name = auto_tag.get('name')
        if not name.startswith('TEMPLATE'):
            print('deleting ' + name + ': ' + object_id)
            delete(endpoint, object_id)


def delete_beta_auto_tags():
    # Safety Check
    if env_name not in ['Personal', 'Demo']:
        print('Error in "delete_beta_auto_tags()" method')
        print('Not for use in this environment')
        print('Env: ' + env)
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_line_number())

    endpoint = '/api/config/v1/autoTags'
    r = get_object_list(endpoint)
    auto_tags_json = json.loads(r.text)
    auto_tag_list = auto_tags_json.get('values')
    for auto_tag in auto_tag_list:
        object_id = auto_tag.get('id')
        name = auto_tag.get('name')
        if name.startswith('BETA'):
            print('deleting ' + name + ': ' + object_id)
            delete(endpoint, object_id)


def delete_request_attributes():
    # Safety Check
    if env_name not in ['Personal', 'Demo']:
        print('Error in "delete_request_attributes()" method')
        print('Not for use in this environment')
        print('Env: ' + env)
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_line_number())

    endpoint = '/api/config/v1/service/requestAttributes'
    r = get_object_list(endpoint)
    request_attributes_json = json.loads(r.text)
    request_attribute_list = request_attributes_json.get('values')
    for request_attribute in request_attribute_list:
        object_id = request_attribute.get('id')
        name = request_attribute.get('name')
        if name.lower() in str(fixed_request_attribute_ids).lower() and not object_id.startswith('aaaaaaaa-bbbb-cccc-dddd'):
            print('deleting ' + name + ': ' + object_id)
            delete(endpoint, object_id)


def report_fixed_id_entities():
    for entity_type, endpoint in [
        ('Auto Tags', '/api/config/v1/autoTags'),
        ('Request Attributes', '/api/config/v1/service/requestAttributes'),
        ('Request Naming Rules', '/api/config/v1/service/requestNaming'),
        ('Host Conditional Naming Rules', '/api/config/v1/conditionalNaming/host'),
        ('Process Group Conditional Naming Rules', '/api/config/v1/conditionalNaming/processGroup'),
        ('Service Conditional Naming Rules', '/api/config/v1/conditionalNaming/service'),
    ]:
        report_fixed_id_entity(entity_type, endpoint)


def report_fixed_id_entity(entity_type, endpoint):
    print(f'{entity_type}:')
    print_lines = []
    r = get_object_list(endpoint)
    entity_json = json.loads(r.text)
    entity_list = entity_json.get('values')
    for entity in entity_list:
        object_id = entity.get('id')
        name = entity.get('name')
        if object_id.startswith('aaaaaaaa-bbbb-cccc-dddd'):
            print_lines.append(name + ': ' + object_id)

    for print_line in sorted(print_lines):
        print(print_line)


def dump_auto_tags():
    print('Auto Tags:')
    print_lines = []
    endpoint = '/api/config/v1/autoTags'
    r = get_object_list(endpoint)
    request_attributes_json = json.loads(r.text)
    request_attribute_list = request_attributes_json.get('values')
    for request_attribute in request_attribute_list:
        object_id = request_attribute.get('id')
        name = request_attribute.get('name')
        # if name.lower() in str(fixed_request_attribute_ids).lower() and not object_id.startswith('aaaaaaaa-bbbb-cccc-dddd'):
        # if not object_id.startswith('aaaaaaaa-bbbb-cccc-dddd'):
        if object_id.startswith('aaaaaaaa-bbbb-cccc-dddd'):
            print_lines.append(name + ': ' + object_id)

    for print_line in sorted(print_lines):
        print(print_line)


def dump_request_attributes():
    print('Request Attributes:')
    print_lines = []
    endpoint = '/api/config/v1/service/requestAttributes'
    r = get_object_list(endpoint)
    request_attributes_json = json.loads(r.text)
    request_attribute_list = request_attributes_json.get('values')
    for request_attribute in request_attribute_list:
        object_id = request_attribute.get('id')
        name = request_attribute.get('name')
        # if name.lower() in str(fixed_request_attribute_ids).lower() and not object_id.startswith('aaaaaaaa-bbbb-cccc-dddd'):
        # if not object_id.startswith('aaaaaaaa-bbbb-cccc-dddd'):
        if object_id.startswith('aaaaaaaa-bbbb-cccc-dddd'):
            print_lines.append(name + ': ' + object_id)

    for print_line in sorted(print_lines):
        print(print_line)


def dump_request_naming_rules_rules():
    print('Request Naming Rules:')
    print_lines = []
    endpoint = '/api/config/v1/service/requestNaming'
    r = get_object_list(endpoint)
    request_naming_json = json.loads(r.text)
    request_attribute_list = request_naming_json.get('values')
    for request_attribute in request_attribute_list:
        object_id = request_attribute.get('id')
        name = request_attribute.get('name')
        # if not object_id.startswith('aaaaaaaa-bbbb-cccc-dddd'):
        # if name.lower() in str(fixed_request_attribute_ids).lower() and not object_id.startswith('aaaaaaaa-bbbb-cccc-dddd'):
        # if True:
        if object_id.startswith('aaaaaaaa-bbbb-cccc-dddd'):
            print_lines.append(name + ': ' + object_id)

    for print_line in sorted(print_lines):
        print(print_line)


def cleanup():
    endpoint = '/api/config/v1/service/requestNaming'
    for object_id in [
        '5265825c-63af-4826-a974-b87ea8d90d86',
    ]:
        delete(endpoint, object_id)


def confirm(message):
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            exit()


def copy_paste_reuse_section():
    print('Never execute this method!  Use for copy/paste reuse and reference only!')
    exit(9999)

    # cleanup()

    # dump_request_attributes()
    # dump_request_naming_rules_rules()

    # confirm('Are you sure you want to delete all BETA tags and post tags them again to PreP?')
    # delete_beta_auto_tags()
    # print('all BETA tags deleted...')
    # # wait for eventual consistency...
    # time.sleep(30)

    # delete_request_attributes()

    # AWS Credential Name Management Zones
    # post_management_zone_aws_credential_name('AWS-NAME')
    # post_management_zone_per_aws_credential_name()

    # CAREFUL!!!
    # Will delete all auto tags that do not start with "TEMPLATE:"
    # delete_auto_tags()

    # Application On Boarding Entities
    # post_management_zone('App:Foo-DEV', [('Application', 'Foo'), ('Environment', 'DEV')])
    # post_management_zone('Env:DEV', [('Environment', 'DEV')])
    # post_management_zone('Env:SIT', [('Environment', 'SIT')])
    # post_management_zone('Env:UAT', [('Environment', 'UAT')])
    # post_management_zone('Env:Prod', [('Environment', 'Prod')])
    # post_management_zone('Env:Stage', [('Environment', 'Stage')])
    # post_management_zone('Infra:Azure', [('Cloud Provider', 'Azure')])
    # post_management_zone('Infra:AWS', [('Cloud Provider', 'AWS')])
    # post_management_zone('Infra:GCP', [('Cloud Provider', 'GCP')])
    # post_management_zone_tag_existence('Infra:On Premise', ['Cloud Provider'], False)
    # post_management_zone_tag_existence('Infra:Kubernetes', ['Kubernetes Cluster'], True)
    # post_web_application_and_detection_rule('Foo', 'foo.com')
    # add_database_relationship_entity_selector_to_tag('5a5651be-b848-4a62-963d-96965f07e55d', 'App', 'bar')

    # Host Group Based Tags
    # put_auto_tags_from_host_groups(['Application', 'Environment'], '_')
    # put_auto_tags_from_host_groups(['Application', 'Function', 'Environment'], '_')
    # put_auto_tags_from_host_groups(['Environment', 'Application', 'Function'], '_')
    # put_auto_tags_from_host_groups(['Environment', 'Application'], '_')

    # DEBUG
    # Can add a web application without a detection rule, but this is not typical
    # post_web_application('Foo')
    # Can add an application detection rule without adding a web application, but this is not typical
    # post_application_detection_rule('APPLICATION-A640A0A73A33F6BA', 'example.com')
    # Just for testing an "internal" method
    # print(build_database_to_relationship_entity_selector('App', 'foo'))
    # Review JSON from GET...
    # dump_json('/api/config/v1/managementZones', '-4003073193108425342')
    # dump_json('/api/config/v1/autoTags', 'c8f19913-b834-3daf-bb76-b4b190372461')

    # These Okta headers may be of use to future clients (no luck at customer_specific)
    # Okta-Request-Id
    # X-Okta-Agent
    # X-Okta-Client-Request-Id
    # X-Okta-User-Agent-Extended
    # From:
    # https://github.com/okta/okta-commons-java/blob/master/http/http-api/src/main/java/com/okta/commons/http/HttpHeaders.java

    # Try Later Maybe
    # {OpenstackAvailabilityZone:Name}
    # {OpenstackZone:Name}
    # {OpenstackComputeNode:Name}
    # {OpenstackProject:Name}
    # OPENSTACK_ACCOUNT_NAME
    # OPENSTACK_ACCOUNT_PROJECT_NAME
    # OPENSTACK_AVAILABILITY_ZONE_NAME
    # OPENSTACK_PROJECT_NAME
    # OPENSTACK_REGION_NAME
    # OPENSTACK_VM_INSTANCE_TYPE
    # OPENSTACK_VM_NAME
    # OPENSTACK_VM_SECURITY_GROUP
    #
    # {Service:IIBApplicationName} Has problems. Tried but no luck on it.
    # {AzureRegion:Name}
    # {CloudFoundryOrganization:Name}
    # {GoogleComputeInstance:Project}
    # {Host:AzureSiteName}

    # customer_specific Opt-Outs:
    # Information not valuable to a wide enough audience:
    # put_auto_tag_host_technology()

    # TODO: Figure why these placeholders are bad:
    # put_auto_tag_typical_process_group_dynamic_key('Java Main CLass', 'JAVA_MAIN_CLASS', '{ProcessGroup:JavaMainCLass}')
    # put_auto_tag_typical_process_group_dynamic_key('Jboss Home', 'JBOSS_HOME', '{ProcessGroup:JbossHome}')
    # put_auto_tag_typical_process_group_dynamic_key('Jboss Mode', 'JBOSS_MODE', '{ProcessGroup:JbossMode}')
    # put_auto_tag_typical_process_group_dynamic_key('Jboss Server Name', 'JBOSS_SERVER_NAME', '{ProcessGroup:JbossServerName}')


if __name__ == '__main__':
    process()
