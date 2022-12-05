import json


def print_header():
    info = data.get('info')
    title = info.get('title')
    description = info.get('description')
    version = info.get('version')
    # header = title + ': ' + description + ' Version: ' + version
    print(title)
    print('')
    print(description)
    print('')
    print('Version: ' + version)
    print('')


def dump_auto_tag_placeholder_list():
    # The placeholders for auto tags are detailed in a description
    description = data.get('components').get('schemas').get('AutoTagRule').get('properties').get('valueFormat').get('description').replace("* `", "").replace("` ", "")
    print('Auto Tag Placeholders:')
    print(description)


def dump_schema_properties_key_enum_list(schema, key):
    print(schema + ':')
    entry_list = data.get('components').get('schemas').get(schema).get('properties').get(key).get('enum')
    for entry in entry_list:
        print(entry)


def dump_endpoint_methods():
    # The endpoint methods
    print('Endpoint Methods:')
    paths = data.get('paths')
    endpoint_methods = {}
    endpoints = list(paths.keys())

    for endpoint in endpoints:
        endpoint_dict = paths.get(endpoint)
        methods = list(endpoint_dict.keys())
        print(endpoint + ': ' + str(methods))
        endpoint_methods[endpoint] = methods


def dump_schema_properties_key_key_enum_list(schema, key1, key2):
    print(schema + ':')
    entry_list = data.get('components').get('schemas').get(schema).get('properties').get(key1).get(key2).get('enum')
    for entry in entry_list:
        print(entry)


def dump_schema_all_of_1_properties_key_enum_list(schema, key):
    print(schema + ':')
    entry_list = data.get('components').get('schemas').get(schema).get('allOf')[1].get('properties').get(key).get('enum')
    for entry in entry_list:
        print(entry)


# Main Processing...
f = open('config_v1_spec3.json',)
data = json.load(f)
print_header()

# dump_endpoint_methods()

# This is where we get all the possible placeholders to use in conditions for process group tag rules
# dump_auto_tag_placeholder_list()

dump_schema_properties_key_enum_list('Placeholder', 'attribute')

# This is where we get all the possible entities to use in conditions for process group tag rules
dump_schema_all_of_1_properties_key_enum_list('ProcessMetadataConditionKey', 'dynamicKey')

# This is where we get other entities to use in conditions for tag rules
dump_schema_properties_key_enum_list('ConditionKey', 'attribute')

# dump_schema_properties_key_enum_list('AlertingPredefinedEventFilter', 'eventType')
# dump_schema_properties_key_enum_list('CalculatedMetricDefinition', 'metric')
# dump_schema_properties_key_enum_list('CustomFilterChartSeriesConfig', 'aggregation')
# dump_schema_properties_key_enum_list('CustomFilterChartSeriesConfig', 'type')
# dump_schema_properties_key_enum_list('CustomFilterConfig', 'type')
# dump_schema_properties_key_enum_list('Extension', 'type')
# dump_schema_properties_key_enum_list('MonitoredEntityFilter', 'type')
# dump_schema_properties_key_enum_list('MzRule', 'type')
# dump_schema_properties_key_enum_list('NotificationConfigStub', 'type')
# dump_schema_properties_key_enum_list('ResourceProvider', 'resourceType')
# dump_schema_properties_key_enum_list('ResourceType', 'primaryResourceType')
# dump_schema_properties_key_enum_list('SimpleHostTech', 'type')
# dump_schema_properties_key_enum_list('SimpleTech', 'type')
# dump_schema_properties_key_enum_list('TagInfo', 'context')
# dump_schema_properties_key_enum_list('Technology', 'type')
# dump_schema_properties_key_enum_list('UniversalTagKey', 'context')
# dump_schema_properties_key_enum_list('WebApplicationMetricDefinition', 'metric')

# dump_schema_all_of_1_properties_key_enum_list('CloudTypeComparison', 'value')
# dump_schema_all_of_1_properties_key_enum_list('FailureReasonComparisonInfo', 'value')
# dump_schema_all_of_1_properties_key_enum_list('HttpMethodComparisonInfo', 'value')
# dump_schema_all_of_1_properties_key_enum_list('HttpStatusClassComparisonInfo', 'value')
# dump_schema_all_of_1_properties_key_enum_list('HypervisorTypeComparision', 'value')
# dump_schema_all_of_1_properties_key_enum_list('IIBInputNodeTypeComparisonInfo', 'value')
# dump_schema_all_of_1_properties_key_enum_list('MobilePlatformComparison', 'value')
# dump_schema_all_of_1_properties_key_enum_list('OsArchitectureComparison', 'value')
# dump_schema_all_of_1_properties_key_enum_list('OsTypeComparison', 'value')
# dump_schema_all_of_1_properties_key_enum_list('PaasTypeComparison', 'value')
# dump_schema_all_of_1_properties_key_enum_list('ServiceTopologyComparison', 'value')
# dump_schema_all_of_1_properties_key_enum_list('ServiceTypeComparisonInfo', 'value')
# dump_schema_all_of_1_properties_key_enum_list('StringComparisonInfo', 'comparison')
# dump_schema_all_of_1_properties_key_enum_list('TagComparisonInfo', 'comparison')

f.close()

# =====================================================================================================================
# Interesting Placeholders
# {AwsAutoScalingGroup:Name}
# {AwsAvailabilityZone:Name}: DONE
# {AwsElasticLoadBalancer:Name}
# {AwsRelationalDatabaseService:DBName}
# {AwsRelationalDatabaseService:Endpoint}
# {AwsRelationalDatabaseService:Engine}
# {AwsRelationalDatabaseService:InstanceClass}
# {AwsRelationalDatabaseService:Name}
# {AwsRelationalDatabaseService:Port}
# {AzureRegion:Name}: PENDING
# {AzureScaleSet:Name}
# {AzureVm:Name}
# {CloudFoundryOrganization:Name}: PENDING
# {CustomDevice:DetectedName}
# {CustomDevice:DnsName}
# {CustomDevice:IpAddress}
# {CustomDevice:Port}
# {DockerContainerGroupInstance:ContainerName}
# {DockerContainerGroupInstance:FullImageName}
# {DockerContainerGroupInstance:ImageVersion}
# {DockerContainerGroupInstance:StrippedImageName}
# {ESXIHost:HardwareModel}
# {ESXIHost:HardwareVendor}
# {ESXIHost:Name}
# {ESXIHost:ProductName}
# {ESXIHost:ProductVersion}
# {Ec2Instance:AmiId}
# {Ec2Instance:BeanstalkEnvironmentName}
# {Ec2Instance:InstanceId}
# {Ec2Instance:InstanceType}
# {Ec2Instance:LocalHostName}
# {Ec2Instance:Name}
# {Ec2Instance:PublicHostName}
# {Ec2Instance:SecurityGroup}
# {GoogleComputeInstance:Id}
# {GoogleComputeInstance:IpAddresses}
# {GoogleComputeInstance:MachineType}
# {GoogleComputeInstance:Name}
# {GoogleComputeInstance:ProjectId}
# {GoogleComputeInstance:Project}: PENDING
# {Host:AWSNameTag}
# {Host:AixLogicalCpuCount}
# {Host:AzureHostName}
# {Host:AzureSiteName}: PENDING
# {Host:BoshDeploymentId}
# {Host:BoshInstanceId}
# {Host:BoshInstanceName}
# {Host:BoshName}
# {Host:BoshStemcellVersion}
# {Host:CpuCores}: PENDING
# {Host:DetectedName}
# {Host:Environment:AppName}
# {Host:Environment:BoshReleaseVersion}
# {Host:Environment:Environment}
# {Host:Environment:Link}
# {Host:Environment:Organization}
# {Host:Environment:Owner}
# {Host:Environment:Support}
# {Host:IpAddress}
# {Host:LogicalCpuCores}
# {Host:OneAgentCustomHostName}
# {Host:OperatingSystemVersion}
# {Host:PaasMemoryLimit}
# {HostGroup:Name}: DONE
# {KubernetesCluster:Name}: OVERLAP?
# {KubernetesNode:DetectedName}: OVERLAP?
# {OpenstackAvailabilityZone:Name}: PENDING
# {OpenstackZone:Name}: PENDING
# {OpenstackComputeNode:Name}
# {OpenstackProject:Name}: PENDING
# {OpenstackVm:UnstanceType}
# {OpenstackVm:Name}
# {OpenstackVm:SecurityGroup}
# {ProcessGroup:AmazonECRImageAccountId}
# {ProcessGroup:AmazonECRImageRegion}
# {ProcessGroup:AmazonECSCluster}
# {ProcessGroup:AmazonECSContainerName}
# {ProcessGroup:AmazonECSFamily}
# {ProcessGroup:AmazonECSRevision}
# {ProcessGroup:AmazonLambdaFunctionName}
# {ProcessGroup:AmazonRegion}
# {ProcessGroup:ApacheConfigPath}
# {ProcessGroup:ApacheSparkMasterIpAddress}
# {ProcessGroup:AspDotNetCoreApplicationPath}
# {ProcessGroup:AspDotNetCoreApplicationPath}
# {ProcessGroup:AzureHostName}
# {ProcessGroup:AzureSiteName}
# {ProcessGroup:CassandraClusterName}
# {ProcessGroup:CatalinaBase}
# {ProcessGroup:CatalinaHome}
# {ProcessGroup:CloudFoundryAppId}
# {ProcessGroup:CloudFoundryAppName}
# {ProcessGroup:CloudFoundryInstanceIndex}
# {ProcessGroup:CloudFoundrySpaceId}
# {ProcessGroup:CloudFoundrySpaceName}
# {ProcessGroup:ColdFusionJvmConfigFile}
# {ProcessGroup:ColdFusionServiceName}
# {ProcessGroup:CommandLineArgs}
# {ProcessGroup:DetectedName}
# {ProcessGroup:DotNetCommandPath}
# {ProcessGroup:DotNetCommand}
# {ProcessGroup:DotNetClusterId}
# {ProcessGroup:DotNetNodeId}
# {ProcessGroup:ElasticsearchClusterName}
# {ProcessGroup:ElasticsearchNodeName}
# {ProcessGroup:EquinoxConfigPath}
# {ProcessGroup:ExeName}
# {ProcessGroup:ExePath}
# {ProcessGroup:GlassFishDomainName}
# {ProcessGroup:GlassFishInstanceName}
# {ProcessGroup:GoogleAppEngineInstance}
# {ProcessGroup:GoogleAppEngineService}
# {ProcessGroup:GoogleCloudProject}
# {ProcessGroup:HybrisBinDirectory}
# {ProcessGroup:HybrisConfigDirectory}
# {ProcessGroup:HybrisConfigDirectory}
# {ProcessGroup:HybrisDataDirectory}
# {ProcessGroup:IBMCicsRegion}
# {ProcessGroup:IBMCtgName}
# {ProcessGroup:IBMImsConnectRegion}
# {ProcessGroup:IBMImsControlRegion}
# {ProcessGroup:IBMImsMessageProcessingRegion}
# {ProcessGroup:IBMImsSoapGwName}
# {ProcessGroup:IBMIntegrationNodeName}
# {ProcessGroup:IBMIntegrationServerName}
# {ProcessGroup:IISAppPool}
# {ProcessGroup:IISRoleName}
# {ProcessGroup:JbossHome}
# {ProcessGroup:JbossMode}
# {ProcessGroup:JbossServerName}
# {ProcessGroup:JavaJarFile}
# {ProcessGroup:JavaJarPath}
# {ProcessGroup:JavaMainCLass}
# {ProcessGroup:KubernetesBasePodName}
# {ProcessGroup:KubernetesContainerName}
# {ProcessGroup:KubernetesFullPodName}
# {ProcessGroup:KubernetesNamespace}
# {ProcessGroup:KubernetesPodUid}
# {ProcessGroup:MssqlInstanceName}
# {ProcessGroup:NodeJsAppBaseDirectory}
# {ProcessGroup:NodeJsAppName}
# {ProcessGroup:NodeJsScriptName}
# {ProcessGroup:OracleSid}
# {ProcessGroup:PHPScriptPath}
# {ProcessGroup:PHPWorkingDirectory}
# {ProcessGroup:Ports}
# {ProcessGroup:RubyAppRootPath}
# {ProcessGroup:RubyScriptPath}
# {ProcessGroup:SoftwareAGInstallRoot}
# {ProcessGroup:SoftwareAGProductPropertyName}
# {ProcessGroup:SpringBootAppName}
# {ProcessGroup:SpringBootProfileName}
# {ProcessGroup:SpringBootStartupClass}
# {ProcessGroup:TIBCOBusinessWorksAppNodeName}
# {ProcessGroup:TIBCOBusinessWorksAppSpaceName}
# {ProcessGroup:TIBCOBusinessWorksCeAppName}
# {ProcessGroup:TIBCOBusinessWorksCeVersion}
# {ProcessGroup:TIBCOBusinessWorksDomainName}
# {ProcessGroup:TIBCOBusinessWorksEnginePropertyFilePath}
# {ProcessGroup:TIBCOBusinessWorksEnginePropertyFile}
# {ProcessGroup:TIBCOBusinessWorksHome}
# {ProcessGroup:VarnishInstanceName}
# {ProcessGroup:WebLogicClusterName}
# {ProcessGroup:WebLogicDomainName}
# {ProcessGroup:WebLogicHome}
# {ProcessGroup:WebLogicName}
# {ProcessGroup:WebSphereCellName}
# {ProcessGroup:WebSphereClusterName}
# {ProcessGroup:WebSphereNodeName}
# {ProcessGroup:WebSphereServerName}
# {ProcessGroup:ActorSystem}
# {Service:STGServerName}
# {Service:DatabaseHostName}
# {Service:DatabaseName}
# {Service:DatabaseVendor}: PENDING
# {Service:DetectedName}
# {Service:EndpointPath}
# {Service:EndpointPathGatewayUrl}
# {Service:IIBApplicationName}: PENDING
# {Service:MessageListenerClassName}
# {Service:Port}
# {Service:PublicDomainName}
# {Service:RemoteEndpoint}
# {Service:RemoteName}
# {Service:WebApplicationId}: PENDING
# {Service:WebContextRoot}: PENDING
# {Service:WebServerName}: PENDING
# {Service:WebServiceNamespace}: PENDING
# {Service:WebServiceName}: PENDING
# {VmwareDatacenter:Name}: PENDING
# {VmwareVm:Name}
#
# Placeholder:
# ACTOR_SYSTEM
# AKKA_ACTOR_CLASS_NAME
# AKKA_ACTOR_MESSAGE_TYPE
# AKKA_ACTOR_PATH
# APPLICATION_BUILD_VERSION
# APPLICATION_ENVIRONMENT
# APPLICATION_NAME
# APPLICATION_RELEASE_VERSION
# AZURE_FUNCTIONS_FUNCTION_NAME
# AZURE_FUNCTIONS_SITE_NAME
# CICS_PROGRAM_NAME
# CICS_SYSTEM_ID
# CICS_TASK_ID
# CICS_TRANSACTION_ID
# CICS_USER_ID
# CPU_TIME
# CTG_GATEWAY_URL
# CTG_PROGRAM
# CTG_SERVER_NAME
# CTG_TRANSACTION_ID
# CUSTOMSERVICE_CLASS
# CUSTOMSERVICE_METHOD
# DATABASE_CHILD_CALL_COUNT
# DATABASE_CHILD_CALL_TIME
# DATABASE_HOST
# DATABASE_NAME
# DATABASE_STATEMENT
# DATABASE_TYPE
# DATABASE_URL
# DISK_IO_TIME
# ERROR_COUNT
# ESB_APPLICATION_NAME
# ESB_INPUT_TYPE
# ESB_LIBRARY_NAME
# ESB_MESSAGE_FLOW_NAME
# EXCEPTION_CLASS
# EXCEPTION_MESSAGE
# FAILED_STATE
# FAILURE_REASON
# FLAW_STATE
# HTTP_REQUEST_METHOD
# HTTP_STATUS
# HTTP_STATUS_CLASS
# IMS_PROGRAM_NAME
# IMS_TRANSACTION_ID
# IMS_USER_ID
# IO_TIME
# IS_KEY_REQUEST
# LAMBDA_COLDSTART
# LOCK_TIME
# MESSAGING_DESTINATION_TYPE
# MESSAGING_IS_TEMPORARY_QUEUE
# MESSAGING_QUEUE_NAME
# MESSAGING_QUEUE_VENDOR
# NETWORK_IO_TIME
# NON_DATABASE_CHILD_CALL_COUNT
# NON_DATABASE_CHILD_CALL_TIME
# PROCESS_GROUP_NAME
# PROCESS_GROUP_TAG
# REMOTE_ENDPOINT
# REMOTE_METHOD
# REMOTE_SERVICE_NAME
# REQUEST_NAME
# REQUEST_TYPE
# RESPONSE_TIME
# RESPONSE_TIME_CLIENT
# RMI_CLASS
# RMI_METHOD
# SERVICE_DISPLAY_NAME
# SERVICE_NAME
# SERVICE_PORT
# SERVICE_PUBLIC_DOMAIN_NAME
# SERVICE_REQUEST_ATTRIBUTE
# SERVICE_TAG
# SERVICE_TYPE
# SERVICE_WEB_APPLICATION_ID
# SERVICE_WEB_CONTEXT_ROOT
# SERVICE_WEB_SERVER_NAME
# SERVICE_WEB_SERVICE_NAME
# SERVICE_WEB_SERVICE_NAMESPACE
# SUSPENSION_TIME
# TOTAL_PROCESSING_TIME
# WAIT_TIME
# WEBREQUEST_QUERY
# WEBREQUEST_RELATIVE_URL
# WEBREQUEST_URL
# WEBREQUEST_URL_HOST
# WEBREQUEST_URL_PATH
# WEBREQUEST_URL_PORT
# WEBSERVICE_ENDPOINT
# WEBSERVICE_METHOD
# ZOS_CALL_TYPE
#
# ProcessMetadataConditionKey:
# AMAZON_ECR_IMAGE_ACCOUNT_ID
# AMAZON_ECR_IMAGE_REGION
# AMAZON_LAMBDA_FUNCTION_NAME
# AMAZON_REGION
# APACHE_CONFIG_PATH
# APACHE_SPARK_MASTER_IP_ADDRESS
# ASP_DOT_NET_CORE_APPLICATION_PATH
# AWS_ECS_CLUSTER
# AWS_ECS_CONTAINERNAME
# AWS_ECS_FAMILY
# AWS_ECS_REVISION
# CASSANDRA_CLUSTER_NAME
# CATALINA_BASE
# CATALINA_HOME
# CLOUD_FOUNDRY_APP_ID
# CLOUD_FOUNDRY_APP_NAME
# CLOUD_FOUNDRY_INSTANCE_INDEX
# CLOUD_FOUNDRY_SPACE_ID
# CLOUD_FOUNDRY_SPACE_NAME
# COLDFUSION_JVM_CONFIG_FILE
# COLDFUSION_SERVICE_NAME
# COMMAND_LINE_ARGS
# CONTAINER_ID
# CONTAINER_IMAGE_NAME
# CONTAINER_IMAGE_VERSION
# DECLARATIVE_ID
# DOTNET_COMMAND
# DOTNET_COMMAND_PATH
# DYNATRACE_CLUSTER_ID
# DYNATRACE_NODE_ID
# ELASTICSEARCH_CLUSTER_NAME
# ELASTICSEARCH_NODE_NAME
# EQUINOX_CONFIG_PATH
# EXE_NAME
# EXE_PATH
# GLASS_FISH_DOMAIN_NAME
# GLASS_FISH_INSTANCE_NAME
# GOOGLE_APP_ENGINE_INSTANCE
# GOOGLE_APP_ENGINE_SERVICE
# GOOGLE_CLOUD_PROJECT
# HYBRIS_BIN_DIRECTORY
# HYBRIS_CONFIG_DIRECTORY
# HYBRIS_DATA_DIRECTORY
# IBM_CICS_REGION
# IBM_CTG_NAME
# IBM_IMS_CONNECT_REGION
# IBM_IMS_CONTROL_REGION
# IBM_IMS_MESSAGE_PROCESSING_REGION
# IBM_IMS_SOAP_GW_NAME
# IBM_INTEGRATION_NODE_NAME
# IBM_INTEGRATION_SERVER_NAME
# IIS_APP_POOL
# IIS_ROLE_NAME
# JAVA_JAR_FILE
# JAVA_JAR_PATH
# JAVA_MAIN_CLASS
# JAVA_MAIN_MODULE
# JBOSS_HOME
# JBOSS_MODE
# JBOSS_SERVER_NAME
# KUBERNETES_BASE_POD_NAME
# KUBERNETES_CONTAINER_NAME
# KUBERNETES_FULL_POD_NAME
# KUBERNETES_NAMESPACE
# KUBERNETES_POD_UID
# KUBERNETES_RULE_RESULT
# MSSQL_INSTANCE_NAME
# NODE_JS_APP_BASE_DIRECTORY
# NODE_JS_APP_NAME
# NODE_JS_SCRIPT_NAME
# ORACLE_SID
# PG_ID_CALC_INPUT_KEY_LINKAGE
# PHP_SCRIPT_PATH
# PHP_WORKING_DIRECTORY
# RUBY_APP_ROOT_PATH
# RUBY_SCRIPT_PATH
# RULE_RESULT
# SOFTWAREAG_INSTALL_ROOT
# SOFTWAREAG_PRODUCTPROPNAME
# SPRINGBOOT_APP_NAME
# SPRINGBOOT_PROFILE_NAME
# SPRINGBOOT_STARTUP_CLASS
# TIBCO_BUSINESSWORKS_CE_APP_NAME
# TIBCO_BUSINESSWORKS_CE_VERSION
# TIBCO_BUSINESS_WORKS_APP_NODE_NAME
# TIBCO_BUSINESS_WORKS_APP_SPACE_NAME
# TIBCO_BUSINESS_WORKS_DOMAIN_NAME
# TIBCO_BUSINESS_WORKS_ENGINE_PROPERTY_FILE
# TIBCO_BUSINESS_WORKS_ENGINE_PROPERTY_FILE_PATH
# TIBCO_BUSINESS_WORKS_HOME
# VARNISH_INSTANCE_NAME
# WEBSPHERE_LIBERTY_SERVER_NAME
# WEB_LOGIC_CLUSTER_NAME
# WEB_LOGIC_DOMAIN_NAME
# WEB_LOGIC_HOME
# WEB_LOGIC_NAME
# WEB_SPHERE_CELL_NAME
# WEB_SPHERE_CLUSTER_NAME
# WEB_SPHERE_NODE_NAME
# WEB_SPHERE_SERVER_NAME

# ConditionKey:
# APPMON_SERVER_NAME
# APPMON_SYSTEM_PROFILE_NAME
# AWS_ACCOUNT_ID
# AWS_ACCOUNT_NAME
# AWS_APPLICATION_LOAD_BALANCER_NAME
# AWS_APPLICATION_LOAD_BALANCER_TAGS
# AWS_AUTO_SCALING_GROUP_NAME
# AWS_AUTO_SCALING_GROUP_TAGS
# AWS_AVAILABILITY_ZONE_NAME
# AWS_CLASSIC_LOAD_BALANCER_FRONTEND_PORTS
# AWS_CLASSIC_LOAD_BALANCER_NAME
# AWS_CLASSIC_LOAD_BALANCER_TAGS
# AWS_NETWORK_LOAD_BALANCER_NAME
# AWS_NETWORK_LOAD_BALANCER_TAGS
# AWS_RELATIONAL_DATABASE_SERVICE_DB_NAME
# AWS_RELATIONAL_DATABASE_SERVICE_ENDPOINT
# AWS_RELATIONAL_DATABASE_SERVICE_ENGINE
# AWS_RELATIONAL_DATABASE_SERVICE_INSTANCE_CLASS
# AWS_RELATIONAL_DATABASE_SERVICE_NAME
# AWS_RELATIONAL_DATABASE_SERVICE_PORT
# AWS_RELATIONAL_DATABASE_SERVICE_TAGS
# AZURE_ENTITY_NAME
# AZURE_ENTITY_TAGS
# AZURE_MGMT_GROUP_NAME
# AZURE_MGMT_GROUP_UUID
# AZURE_REGION_NAME
# AZURE_SCALE_SET_NAME
# AZURE_SUBSCRIPTION_NAME
# AZURE_SUBSCRIPTION_UUID
# AZURE_TENANT_NAME
# AZURE_TENANT_UUID
# AZURE_VM_NAME
# BROWSER_MONITOR_NAME
# BROWSER_MONITOR_TAGS
# CLOUD_APPLICATION_LABELS
# CLOUD_APPLICATION_NAME
# CLOUD_APPLICATION_NAMESPACE_LABELS
# CLOUD_APPLICATION_NAMESPACE_NAME
# CLOUD_FOUNDRY_FOUNDATION_NAME
# CLOUD_FOUNDRY_ORG_NAME
# CUSTOM_APPLICATION_NAME
# CUSTOM_APPLICATION_PLATFORM
# CUSTOM_APPLICATION_TAGS
# CUSTOM_APPLICATION_TYPE
# CUSTOM_DEVICE_DETECTED_NAME
# CUSTOM_DEVICE_DNS_ADDRESS
# CUSTOM_DEVICE_GROUP_NAME
# CUSTOM_DEVICE_GROUP_TAGS
# CUSTOM_DEVICE_IP_ADDRESS
# CUSTOM_DEVICE_METADATA
# CUSTOM_DEVICE_NAME
# CUSTOM_DEVICE_PORT
# CUSTOM_DEVICE_TAGS
# CUSTOM_DEVICE_TECHNOLOGY
# DATA_CENTER_SERVICE_DECODER_TYPE
# DATA_CENTER_SERVICE_IP_ADDRESS
# DATA_CENTER_SERVICE_METADATA
# DATA_CENTER_SERVICE_NAME
# DATA_CENTER_SERVICE_PORT
# DATA_CENTER_SERVICE_TAGS
# DOCKER_CONTAINER_NAME
# DOCKER_FULL_IMAGE_NAME
# DOCKER_IMAGE_VERSION
# DOCKER_STRIPPED_IMAGE_NAME
# EC2_INSTANCE_AMI_ID
# EC2_INSTANCE_AWS_INSTANCE_TYPE
# EC2_INSTANCE_AWS_SECURITY_GROUP
# EC2_INSTANCE_BEANSTALK_ENV_NAME
# EC2_INSTANCE_ID
# EC2_INSTANCE_NAME
# EC2_INSTANCE_PRIVATE_HOST_NAME
# EC2_INSTANCE_PUBLIC_HOST_NAME
# EC2_INSTANCE_TAGS
# ENTERPRISE_APPLICATION_DECODER_TYPE
# ENTERPRISE_APPLICATION_IP_ADDRESS
# ENTERPRISE_APPLICATION_METADATA
# ENTERPRISE_APPLICATION_NAME
# ENTERPRISE_APPLICATION_PORT
# ENTERPRISE_APPLICATION_TAGS
# ESXI_HOST_CLUSTER_NAME
# ESXI_HOST_HARDWARE_MODEL
# ESXI_HOST_HARDWARE_VENDOR
# ESXI_HOST_NAME
# ESXI_HOST_PRODUCT_NAME
# ESXI_HOST_PRODUCT_VERSION
# ESXI_HOST_TAGS
# EXTERNAL_MONITOR_ENGINE_DESCRIPTION
# EXTERNAL_MONITOR_ENGINE_NAME
# EXTERNAL_MONITOR_ENGINE_TYPE
# EXTERNAL_MONITOR_NAME
# EXTERNAL_MONITOR_TAGS
# GEOLOCATION_SITE_NAME
# GOOGLE_CLOUD_PLATFORM_ZONE_NAME
# GOOGLE_COMPUTE_INSTANCE_ID
# GOOGLE_COMPUTE_INSTANCE_MACHINE_TYPE
# GOOGLE_COMPUTE_INSTANCE_NAME
# GOOGLE_COMPUTE_INSTANCE_PROJECT
# GOOGLE_COMPUTE_INSTANCE_PROJECT_ID
# GOOGLE_COMPUTE_INSTANCE_PUBLIC_IP_ADDRESSES
# HOST_AIX_LOGICAL_CPU_COUNT
# HOST_AIX_SIMULTANEOUS_THREADS
# HOST_AIX_VIRTUAL_CPU_COUNT
# HOST_ARCHITECTURE
# HOST_AWS_NAME_TAG
# HOST_AZURE_COMPUTE_MODE
# HOST_AZURE_SKU
# HOST_AZURE_WEB_APPLICATION_HOST_NAMES
# HOST_AZURE_WEB_APPLICATION_SITE_NAMES
# HOST_BITNESS
# HOST_BOSH_AVAILABILITY_ZONE
# HOST_BOSH_DEPLOYMENT_ID
# HOST_BOSH_INSTANCE_ID
# HOST_BOSH_INSTANCE_NAME
# HOST_BOSH_NAME
# HOST_BOSH_STEMCELL_VERSION
# HOST_CLOUD_TYPE
# HOST_CPU_CORES
# HOST_CUSTOM_METADATA
# HOST_DETECTED_NAME
# HOST_GROUP_ID
# HOST_GROUP_NAME
# HOST_HYPERVISOR_TYPE
# HOST_IP_ADDRESS
# HOST_KUBERNETES_LABELS
# HOST_LOGICAL_CPU_CORES
# HOST_NAME
# HOST_ONEAGENT_CUSTOM_HOST_NAME
# HOST_OS_TYPE
# HOST_OS_VERSION
# HOST_PAAS_MEMORY_LIMIT
# HOST_PAAS_TYPE
# HOST_TAGS
# HOST_TECHNOLOGY
# HTTP_MONITOR_NAME
# HTTP_MONITOR_TAGS
# KUBERNETES_CLUSTER_NAME
# KUBERNETES_NODE_NAME
# MOBILE_APPLICATION_NAME
# MOBILE_APPLICATION_PLATFORM
# MOBILE_APPLICATION_TAGS
# NAME_OF_COMPUTE_NODE
# OPENSTACK_ACCOUNT_NAME
# OPENSTACK_ACCOUNT_PROJECT_NAME
# OPENSTACK_AVAILABILITY_ZONE_NAME
# OPENSTACK_PROJECT_NAME
# OPENSTACK_REGION_NAME
# OPENSTACK_VM_INSTANCE_TYPE
# OPENSTACK_VM_NAME
# OPENSTACK_VM_SECURITY_GROUP
# PROCESS_GROUP_AZURE_HOST_NAME
# PROCESS_GROUP_AZURE_SITE_NAME
# PROCESS_GROUP_CUSTOM_METADATA
# PROCESS_GROUP_DETECTED_NAME
# PROCESS_GROUP_ID
# PROCESS_GROUP_LISTEN_PORT
# PROCESS_GROUP_NAME
# PROCESS_GROUP_PREDEFINED_METADATA
# PROCESS_GROUP_TAGS
# PROCESS_GROUP_TECHNOLOGY
# PROCESS_GROUP_TECHNOLOGY_EDITION
# PROCESS_GROUP_TECHNOLOGY_VERSION
# QUEUE_NAME
# QUEUE_TECHNOLOGY
# QUEUE_VENDOR
# SERVICE_AKKA_ACTOR_SYSTEM
# SERVICE_CTG_SERVICE_NAME
# SERVICE_DATABASE_HOST_NAME
# SERVICE_DATABASE_NAME
# SERVICE_DATABASE_TOPOLOGY
# SERVICE_DATABASE_VENDOR
# SERVICE_DETECTED_NAME
# SERVICE_ESB_APPLICATION_NAME
# SERVICE_IBM_CTG_GATEWAY_URL
# SERVICE_IIB_APPLICATION_NAME
# SERVICE_MESSAGING_LISTENER_CLASS_NAME
# SERVICE_NAME
# SERVICE_PORT
# SERVICE_PUBLIC_DOMAIN_NAME
# SERVICE_REMOTE_ENDPOINT
# SERVICE_REMOTE_SERVICE_NAME
# SERVICE_TAGS
# SERVICE_TECHNOLOGY
# SERVICE_TECHNOLOGY_EDITION
# SERVICE_TECHNOLOGY_VERSION
# SERVICE_TOPOLOGY
# SERVICE_TYPE
# SERVICE_WEB_APPLICATION_ID
# SERVICE_WEB_CONTEXT_ROOT
# SERVICE_WEB_SERVER_ENDPOINT
# SERVICE_WEB_SERVER_NAME
# SERVICE_WEB_SERVICE_NAME
# SERVICE_WEB_SERVICE_NAMESPACE
# VMWARE_DATACENTER_NAME
# VMWARE_VM_NAME
# WEB_APPLICATION_NAME
# WEB_APPLICATION_NAME_PATTERN
# WEB_APPLICATION_TAGS
# WEB_APPLICATION_TYPE
