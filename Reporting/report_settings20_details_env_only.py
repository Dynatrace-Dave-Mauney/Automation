import dynatrace_rest_api_helper
import os
import urllib.parse


schema_defaults = {
    'builtin:alerting.profile': [
        "{'name': 'Default', 'severityRules': [{'severityLevel': 'ERRORS', 'delayInMinutes': 0, 'tagFilterIncludeMode': 'NONE'}, {'severityLevel': 'MONITORING_UNAVAILABLE', 'delayInMinutes': 0, 'tagFilterIncludeMode': 'NONE'}, {'severityLevel': 'CUSTOM_ALERT', 'delayInMinutes': 0, 'tagFilterIncludeMode': 'NONE'}, {'severityLevel': 'AVAILABILITY', 'delayInMinutes': 0, 'tagFilterIncludeMode': 'NONE'}, {'severityLevel': 'RESOURCE_CONTENTION', 'delayInMinutes': 30, 'tagFilterIncludeMode': 'NONE'}, {'severityLevel': 'PERFORMANCE', 'delayInMinutes': 30, 'tagFilterIncludeMode': 'NONE'}], 'eventFilters': []}"],
    'builtin:anomaly-detection.frequent-issues': [
        "{'detectFrequentIssuesInApplications': True, 'detectFrequentIssuesInTransactionsAndServices': True, 'detectFrequentIssuesInInfrastructure': True}"],
    'builtin:container.technology': [
        "{'boshProcessManager': True, 'containerd': True, 'crio': True, 'docker': True, 'dockerWindows': False, 'garden': True, 'winc': False}"],
    'builtin:elasticsearch.user-session-export-settings': [
        "{'values': [{'endpointDefinition': {'enableUserSessionExport': True, 'contentType': 'application/json', 'usePost': False}, 'authentication': {'active': False, 'basicAuth': {'username': '', 'password': ''}}, 'sendDirect': {'active': False}, 'exportBehavior': {'disableNotification': False, 'customConfiguration': ''}}]}"],
    'builtin:eula-settings': ["{'enableEula': False}"],
    'builtin:logmonitoring.log-events': [
        '{\'enabled\': True, \'summary\': \'Default Kubernetes Log Events\', \'query\': \'event.type="k8s"\', \'eventTemplate\': {\'title\': \'{content}\', \'description\': \'\', \'eventType\': \'INFO\', \'metadata\': [{\'metadataKey\': \'dt.entity.cloud_application_instance\', \'metadataValue\': \'{dt.entity.cloud_application_instance}\'}, {\'metadataKey\': \'dt.kubernetes.event.reason\', \'metadataValue\': \'{dt.kubernetes.event.reason}\'}, {\'metadataKey\': \'status\', \'metadataValue\': \'{status}\'}, {\'metadataKey\': \'dt.event.group_label\', \'metadataValue\': \'{dt.kubernetes.event.reason}\'}, {\'metadataKey\': \'dt.kubernetes.event.involved_object.kind\', \'metadataValue\': \'{dt.kubernetes.event.involved_object.kind}\'}, {\'metadataKey\': \'k8s.pod.name\', \'metadataValue\': \'{k8s.pod.name}\'}, {\'metadataKey\': \'dt.kubernetes.workload.name\', \'metadataValue\': \'{dt.kubernetes.workload.name}\'}, {\'metadataKey\': \'dt.kubernetes.event.message\', \'metadataValue\': \'{content}\'}, {\'metadataKey\': \'dt.entity.cloud_application_namespace\', \'metadataValue\': \'{dt.entity.cloud_application_namespace}\'}, {\'metadataKey\': \'dt.event.is_rootcause_relevant\', \'metadataValue\': \'{dt.events.root_cause_relevant}\'}, {\'metadataKey\': \'dt.kubernetes.cluster.name\', \'metadataValue\': \'{dt.kubernetes.cluster.name}\'}, {\'metadataKey\': \'k8s.namespace.name\', \'metadataValue\': \'{k8s.namespace.name}\'}, {\'metadataKey\': \'dt.entity.kubernetes_node\', \'metadataValue\': \'{dt.entity.kubernetes_node}\'}, {\'metadataKey\': \'dt.kubernetes.event.involved_object.name\', \'metadataValue\': \'{dt.kubernetes.event.involved_object.name}\'}, {\'metadataKey\': \'dt.kubernetes.node.name\', \'metadataValue\': \'{dt.kubernetes.node.name}\'}, {\'metadataKey\': \'dt.entity.kubernetes_cluster\', \'metadataValue\': \'{dt.entity.kubernetes_cluster}\'}, {\'metadataKey\': \'dt.entity.cloud_application\', \'metadataValue\': \'{dt.entity.cloud_application}\'}]}}'],
    'builtin:mainframe.mqfilters': [
        "{'cicsMqQueueIdIncludes': [], 'cicsMqQueueIdExcludes': [], 'imsMqQueueIdIncludes': [], 'imsMqQueueIdExcludes': [], 'imsCrTrnIdIncludes': [], 'imsCrTrnIdExcludes': []}"],
    'builtin:mainframe.txmonitoring': [
        "{'monitorAllIncomingWebRequests': False, 'groupCicsRegions': True, 'nodeLimit': 500}"],
    'builtin:mainframe.txstartfilters': [
        "{'includedCicsTerminalTransactionIds': [], 'includedCicsTransactionIds': [], 'includedImsTransactionIds': []}"],
    'builtin:monitoredentities.generic.type': [
        "{'enabled': True, 'name': 'span:service', 'displayName': 'Span Service', 'createdBy': 'Dynatrace', 'rules': [{'idPattern': '{service.name}', 'instanceNamePattern': '{service.name}', 'sources': [{'sourceType': 'Metrics', 'condition': '$eq(builtin:span_responsetime)'}, {'sourceType': 'Metrics', 'condition': '$eq(builtin:span_throughput)'}, {'sourceType': 'Spans'}, {'sourceType': 'Metrics', 'condition': '$eq(builtin:span_failure_rate)'}], 'requiredDimensions': [], 'attributes': [{'key': 'servicename', 'displayName': 'Service Name', 'pattern': '{service.name}'}]}]}"],
    'builtin:preferences.privacy': [
        "{'masking': {'ipAddressMaskingEnabled': True, 'ipAddressMasking': 'all', 'personalDataUriMaskingEnabled': False, 'userActionMaskingEnabled': False}, 'userTracking': {'persistentCookieEnabled': False}, 'dataCollection': {'optInModeEnabled': False}, 'doNotTrack': {'complyWithDoNotTrack': True, 'doNotTrack': 'anonymous'}}"],
    'builtin:process-group.detection-flags': [
        "{'ignoreUniqueIdentifiers': True, 'useCatalinaBase': False, 'useDockerContainerName': False, 'autoDetectCassandraClusters': True, 'addNodeJsScriptName': True, 'autoDetectTibcoEngines': True, 'identifyJbossServerBySystemProperty': True, 'autoDetectWebMethodsIntegrationServer': True, 'autoDetectSpringBoot': True, 'autoDetectTibcoContainerEditionEngines': True}"],
    'builtin:process.built-in-process-monitoring-rule': [
        "{'-2': True, '-3': True, '-4': True, '-49': True, '-50': True, '-51': True, '-52': True, '-53': True, '-54': True, '-47': True, '-5': True, '-6': True, '-7': True, '-8': True, '-9': True, '-10': True, '-11': True, '-12': True, '-13': True, '-14': True, '-16': True, '-17': True, '-18': True, '-19': True, '-20': True, '-21': True, '-22': True, '-23': True, '-24': True, '-25': True, '-26': True, '-27': True, '-28': True, '-29': True, '-45': True, '-32': True, '-33': True, '-34': True, '-35': True, '-36': True, '-55': True, '-56': True, '-43': True, '-37': True, '-38': True, '-39': True, '-44': True, '-40': True, '-41': True, '-46': True, '-48': True, '-57': True, '-58': True, '-59': True, '-60': True, '-61': True, '-62': True, '-63': True, '-64': True, '-65': True, '-66': True}"],
    'builtin:process.custom-process-monitoring-rule': [
        "{'enabled': True, 'mode': 'MONITORING_OFF', 'condition': {'item': 'EXE_NAME', 'operator': 'STARTS', 'value': 'Tanium'}}"],
    'builtin:process.process-monitoring': ["{'autoMonitoring': True}"],
    'builtin:resource-attribute': [
        "{'attributeKeys': [{'enabled': True, 'attributeKey': 'service.name'}, {'enabled': True, 'attributeKey': 'dt.entity.process_group_instance'}, {'enabled': True, 'attributeKey': 'dt.entity.host'}]}"],
    'builtin:rum.host-headers': ["{'headerName': 'X-Forwarded-Host'}", "{'headerName': 'X-Host'}",
                                 "{'headerName': 'Host'}"],
    'builtin:rum.ip-determination': ["{'headerName': 'rproxy_remote_address'}", "{'headerName': 'True-Client-IP'}",
                                     "{'headerName': 'X-Client-Ip'}", "{'headerName': 'X-Cluster-Client-Ip'}",
                                     "{'headerName': 'X-Forwarded-For'}", "{'headerName': 'X-Http-Client-Ip'}",
                                     "{'headerName': 'CF-Connecting-IP'}"],
    'builtin:rum.user-experience-score': [
        "{'considerLastAction': True, 'considerRageClick': True, 'maxFrustratedUserActionsThreshold': 30, 'minSatisfiedUserActionsThreshold': 50}"],
    'builtin:span-entry-points': [
        "{'entryPointRule': {'ruleName': 'Suppress client spans', 'ruleAction': 'DONT_CREATE_ENTRYPOINT', 'matchers': [{'source': 'SPAN_KIND', 'type': 'EQUALS', 'spanKindValue': 'CLIENT'}]}}",
        "{'entryPointRule': {'ruleName': 'Suppress internal spans', 'ruleAction': 'DONT_CREATE_ENTRYPOINT', 'matchers': [{'source': 'SPAN_KIND', 'type': 'EQUALS', 'spanKindValue': 'INTERNAL'}]}}",
        "{'entryPointRule': {'ruleName': 'Suppress producer spans', 'ruleAction': 'DONT_CREATE_ENTRYPOINT', 'matchers': [{'source': 'SPAN_KIND', 'type': 'EQUALS', 'spanKindValue': 'PRODUCER'}]}}"],
    'builtin:monitoredentities.generic.relation': [
        "{'enabled': True, 'sources': [{'sourceType': 'Spans'}], 'createdBy': 'Dynatrace', 'fromType': 'span:service', 'typeOfRelation': 'RUNS_ON', 'toType': 'process_group_instance'}",
        "{'enabled': True, 'sources': [{'sourceType': 'Spans'}], 'createdBy': 'Dynatrace', 'fromType': 'span:service', 'typeOfRelation': 'RUNS_ON', 'toType': 'host'}"],
    'builtin:span-event-attribute': ["{'key': 'exception.escaped'}", "{'key': 'exception.message'}",
                                     "{'key': 'exception.stacktrace'}", "{'key': 'exception.type'}"],
    'builtin:anomaly-detection.rum-custom-crash-rate-increase': [
        "{'crashRateIncrease': {'enabled': True, 'detectionMode': 'auto', 'crashRateIncreaseAuto': {'baselineViolationPercentage': 150.0, 'concurrentUsers': 5.0, 'sensitivity': 'low'}}}"],
    'builtin:process-group.cloud-application-workload-detection': ["{'enabled': True, 'filters': []}"],
    'builtin:anomaly-detection.rum-custom': [
        "{'errorRateIncrease': {'enabled': True, 'detectionMode': 'auto', 'errorRateIncreaseAuto': {'thresholdAbsolute': 5.0, 'thresholdRelative': 50.0}}, 'slowUserActions': {'enabled': True, 'detectionMode': 'auto', 'slowUserActionsAuto': {'durationThresholdAll': {'durationThreshold': 100.0, 'slowdownPercentage': 50.0}, 'durationThresholdSlowest': {'durationThreshold': 1000.0, 'slowdownPercentage': 100.0}, 'durationAvoidOveralerting': {'minActionRate': 10}}}, 'unexpectedLowLoad': {'enabled': True, 'thresholdPercentage': 50.0}, 'unexpectedHighLoad': {'enabled': False}}"],
    'builtin:networkzones': ["{'enabled': True}"],
    'builtin:apis.detection-rules': [
        "{'apiName': 'Built-In JRE', 'apiColor': '#c95218', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'javax.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'java.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'sun.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.oracle.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'jdk.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.sun.'}]}",
        "{'apiName': 'Built-In Java Cassandra', 'apiColor': '#debbf3', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.datastax.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.netflix.astyanax.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'org.apache.cassandra.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'me.prettyprint.cassandra.'}]}",
        "{'apiName': 'Built-In Apache', 'apiColor': '#2ab6f4', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'org.apache.'}]}",
        "{'apiName': 'Built-In Java IBM CTG', 'apiColor': '#c9a000', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.ibm.ctg.'}]}",
        "{'apiName': 'Built-In Hibernate', 'apiColor': '#522273', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'org.hibernate.'}]}",
        "{'apiName': 'Built-In Java IBM MQ', 'apiColor': '#ffd0ab', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.ibm.mq.'}]}",
        "{'apiName': 'Built-In Java tests', 'apiColor': '#008cdb', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'org.junit.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'junit.framework.'}]}",
        "{'apiName': 'Built-In JBoss', 'apiColor': '#fff29a', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'org.jboss.'}]}",
        "{'apiName': 'Built-In Java MongoDB', 'apiColor': '#fff29a', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.mongodb.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.novus.casbah.mongodb.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'org.bson.'}]}",
        "{'apiName': 'Built-In Mule', 'apiColor': '#008cdb', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'org.mule.'}]}",
        "{'apiName': 'Built-In Java RabbitMQ', 'apiColor': '#aeebf0', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.rabbitmq.'}]}",
        "{'apiName': 'Built-In Spring', 'apiColor': '#debbf3', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'org.springframework.'}]}",
        "{'apiName': 'Built-In TIBCO', 'apiColor': '#a972cc', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'org.tibco.'}]}",
        "{'apiName': 'Built-In Oracle WebLogic', 'apiColor': '#7c38a1', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.weblogic.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'bea.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.bea.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'weblogic.'}]}",
        "{'apiName': 'Built-In IBM WebSphere', 'apiColor': '#4fd5e0', 'technology': 'Java', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'com.ibm.websphere.'}]}",
        "{'apiName': 'Built-In Go Standard Library', 'apiColor': '#4fd5e0', 'technology': 'Go', 'thirdPartyApi': True, 'conditions': [{'base': 'PACKAGE', 'matcher': 'BEGINS_WITH', 'pattern': 'sync'}, {'base': 'PACKAGE', 'matcher': 'BEGINS_WITH', 'pattern': 'runtime'}, {'base': 'PACKAGE', 'matcher': 'BEGINS_WITH', 'pattern': 'io'}, {'base': 'PACKAGE', 'matcher': 'BEGINS_WITH', 'pattern': 'net'}, {'base': 'PACKAGE', 'matcher': 'BEGINS_WITH', 'pattern': 'os'}]}",
        "{'apiName': 'Built-In Go Database', 'apiColor': '#fff29a', 'technology': 'Go', 'thirdPartyApi': True, 'conditions': [{'base': 'PACKAGE', 'matcher': 'BEGINS_WITH', 'pattern': 'database'}]}",
        "{'apiName': 'Built-In .NET CLR', 'apiColor': '#7c38a1', 'technology': 'dotNet', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'System.'}]}",
        "{'apiName': 'Built-In .NET Entity Framework Core', 'apiColor': '#4fd5e0', 'technology': 'dotNet', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'Microsoft.EntityFrameworkCore.'}]}",
        "{'apiName': 'Built-In .NET Logging', 'apiColor': '#ffa86c', 'technology': 'dotNet', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'log4net.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'Microsoft.Practices.EnterpriseLibrary.Logging.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'Microsoft.EnterpriseInstrumentation.EventSource.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'Microsoft.Extensions.Logging.'}]}",
        "{'apiName': 'Built-In .NET Azure Service Fabric', 'apiColor': '#fff29a', 'technology': 'dotNet', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'Microsoft.ServiceFabric.'}]}",
        "{'apiName': 'Built-In ASP.NET Core', 'apiColor': '#008cdb', 'technology': 'dotNet', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'Microsoft.AspNetCore.'}]}",
        "{'apiName': 'Built-In .NET RabbitMQ', 'apiColor': '#aeebf0', 'technology': 'dotNet', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'RabbitMQ.'}]}",
        "{'apiName': 'Built-In .NET IBM MQ', 'apiColor': '#ffd0ab', 'technology': 'dotNet', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'IBM.WMQ.'}, {'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'IBM.XMS.'}]}",
        "{'apiName': 'Built-In .NET MongoDB', 'apiColor': '#fff29a', 'technology': 'dotNet', 'thirdPartyApi': True, 'conditions': [{'base': 'FQCN', 'matcher': 'BEGINS_WITH', 'pattern': 'MongoDB.'}]}",
        "{'apiName': 'Built-In Wordpress', 'apiColor': '#b4e5f9', 'technology': 'PHP', 'thirdPartyApi': True, 'conditions': [{'base': 'FILE_NAME', 'matcher': 'CONTAINS', 'pattern': 'wp-includes/'}]}"],
    'builtin:anomaly-detection.infrastructure-disks': [
        "{'disk': {'diskLowSpaceDetection': {'enabled': True, 'detectionMode': 'auto'}, 'diskSlowWritesAndReadsDetection': {'enabled': True, 'detectionMode': 'auto'}, 'diskLowInodesDetection': {'enabled': True, 'detectionMode': 'auto'}}}"],
    'builtin:anomaly-detection.infrastructure-disks': [
        "{'disk': {'diskLowSpaceDetection': {'enabled': True, 'detectionMode': 'auto'}, 'diskSlowWritesAndReadsDetection': {'enabled': True, 'detectionMode': 'auto'}, 'diskLowInodesDetection': {'enabled': True, 'detectionMode': 'auto'}}}"],
    'builtin:os-services-monitoring': [
        "{'enabled': False, 'system': 'LINUX', 'name': 'Auto-start Linux OS Services', 'alerting': True, 'monitoring': False, 'statusConditionLinux': '$eq(failed)', 'detectionConditionsLinux': [{'property': 'StartupType', 'startupCondition': '$eq(enabled)'}]}",
        "{'enabled': False, 'system': 'WINDOWS', 'name': 'Auto-start Windows OS Services', 'alerting': True, 'monitoring': False, 'statusConditionWindows': '$not($eq(running))', 'detectionConditionsWindows': [{'property': 'StartupType', 'startupCondition': '$eq(auto)'}]}"],
    'builtin:anomaly-detection.infrastructure-hosts': [
        "{'host': {'connectionLostDetection': {'enabled': True, 'onGracefulShutdowns': 'DONT_ALERT_ON_GRACEFUL_SHUTDOWN'}, 'highCpuSaturationDetection': {'enabled': True, 'detectionMode': 'auto'}, 'highMemoryDetection': {'enabled': True, 'detectionMode': 'auto'}, 'highGcActivityDetection': {'enabled': True, 'detectionMode': 'auto'}, 'outOfMemoryDetection': {'enabled': True, 'detectionMode': 'auto'}, 'outOfThreadsDetection': {'enabled': True, 'detectionMode': 'auto'}}, 'network': {'networkDroppedPacketsDetection': {'enabled': True, 'detectionMode': 'auto'}, 'networkErrorsDetection': {'enabled': True, 'detectionMode': 'auto'}, 'highNetworkDetection': {'enabled': True, 'detectionMode': 'auto'}, 'networkTcpProblemsDetection': {'enabled': True, 'detectionMode': 'auto'}, 'networkHighRetransmissionDetection': {'enabled': True, 'detectionMode': 'auto'}}}"],
    'builtin:anomaly-detection.infrastructure-vmware': [
        "{'esxiHighCpuDetection': {'enabled': True, 'detectionMode': 'auto'}, 'guestCpuLimitDetection': {'enabled': True, 'detectionMode': 'auto'}, 'esxiHighMemoryDetection': {'enabled': True, 'detectionMode': 'auto'}, 'overloadedStorageDetection': {'enabled': True, 'detectionMode': 'auto'}, 'undersizedStorageDetection': {'enabled': True, 'detectionMode': 'auto'}, 'slowPhysicalStorageDetection': {'enabled': True, 'detectionMode': 'auto'}, 'droppedPacketsDetection': {'enabled': True, 'detectionMode': 'auto'}, 'lowDatastoreSpaceDetection': {'enabled': True, 'detectionMode': 'auto'}}"],
    'builtin:anomaly-detection.infrastructure-aws': [
        "{'ec2CandidateHighCpuDetection': {'enabled': True, 'detectionMode': 'auto'}, 'rdsHighCpuDetection': {'enabled': True, 'detectionMode': 'auto'}, 'rdsHighWriteReadLatencyDetection': {'enabled': True, 'detectionMode': 'auto'}, 'rdsLowStorageDetection': {'enabled': True, 'detectionMode': 'auto'}, 'rdsHighMemoryDetection': {'enabled': True, 'detectionMode': 'auto'}, 'elbHighConnectionErrorsDetection': {'enabled': True, 'detectionMode': 'auto'}, 'rdsRestartsSequenceDetection': {'enabled': True, 'detectionMode': 'auto'}, 'lambdaHighErrorRateDetection': {'enabled': True, 'detectionMode': 'auto'}}"],
    'builtin:anomaly-detection.rum-web': [
        "{'responseTime': {'enabled': True, 'detectionMode': 'auto', 'responseTimeAuto': {'responseTimeAll': {'degradationMilliseconds': 100.0, 'degradationPercent': 50.0}, 'responseTimeSlowest': {'slowestDegradationMilliseconds': 1000.0, 'slowestDegradationPercent': 100.0}, 'overAlertingProtection': {'actionsPerMinute': 10.0, 'minutesAbnormalState': 1.0}}}, 'errorRate': {'enabled': True, 'errorRateDetectionMode': 'auto', 'errorRateAuto': {'absoluteIncrease': 5.0, 'relativeIncrease': 50.0, 'overAlertingProtection': {'actionsPerMinute': 10.0, 'minutesAbnormalState': 1.0}}}, 'trafficDrops': {'enabled': True, 'trafficDrops': {'trafficDropPercentage': 50.0, 'abnormalStateAbnormalState': 1.0}}, 'trafficSpikes': {'enabled': False}}"],
}

schema_expected_empty = [
    'builtin:accounting.ddu.limit',
    'builtin:alerting.maintenance-window',
    'builtin:anomaly-detection.databases',
    'builtin:anomaly-detection.services',
    'builtin:container.built-in-monitoring-rule',
    'builtin:container.monitoring-rule',
    'builtin:custom-metrics',
    'builtin:dashboards.general',
    'builtin:dashboards.presets',
    'builtin:declarativegrouping',
    'builtin:deployment.management.update-windows',
    'builtin:disk.options',
    'builtin:host.process-groups.monitoring-state',
    'builtin:ibmmq.queue-sharing-group',
    'builtin:issue-tracking.integration',
    'builtin:logmonitoring.schemaless-log-metric',
    'builtin:metric.metadata',
    'builtin:metric.query',
    'builtin:monitoring.slo',
    'builtin:monitoring.slo.normalization',
    'builtin:mrum.request-errors',
    'builtin:os.services.monitoring',
    'builtin:problem.notifications',
    'builtin:process-group.advanced-detection-rule',
    'builtin:process-group.monitoring.state',
    'builtin:process-group.simple-detection-rule',
    'builtin:rum.processgroup',
    'builtin:rum.resource-timing-origins',
    'builtin:rum.web.beacon-domain-origins',
    'builtin:rum.web.resource-cleanup-rules',
    'builtin:rum.web.resource-types',
    'builtin:settings.mutedrequests',
    'builtin:settings.subscriptions.service',
    'builtin:span-attribute',
    'builtin:span-capturing',
    'builtin:span-context-propagation',
    'builtin:synthetic.browser.outage-handling',
    'builtin:synthetic.browser.performance-thresholds',
    'builtin:synthetic.http.outage-handling',
    'builtin:synthetic.http.performance-thresholds',
    'builtin:synthetic.synthetic-availability-settings',
    'builtin:tokens.token-settings',
    'builtin:user-settings',
    'builtin:cloud.kubernetes',
    'builtin:rum.provider-breakdown',
    'builtin:nettracer.traffic',
    'builtin:rum.web.ipaddress-exclusion',
    'builtin:logmonitoring.log-custom-attributes',
    'builtin:rum.web.browser-exclusion',
    'builtin:ibmmq.queue-managers',
    'builtin:rum.mobile.enablement',
    'builtin:rum.web.request-errors',
    'builtin:synthetic.browser.name',
    'builtin:rum.mobile.key-performance-metrics',
    'builtin:rum.mobile.request-errors',
    'builtin:rum.mobile.name',
    'builtin:custom-unit',
    'builtin:rum.mobile.privacy',
    'builtin:synthetic.http.name',
    'builtin:process-visibility',
    'ext:com.dynatrace.extension.f5.bigip',
    'builtin:logmonitoring.log-agent-configuration',
    'builtin:rum.web.name',
    'builtin:synthetic.http.scheduling',
    'builtin:rum.web.custom-errors',
    'builtin:rum.mobile.beacon-endpoint',
    'builtin:anomaly-detection.rum-mobile',
    'builtin:sessionreplay.web.privacy-preferences',
    'builtin:rum.web.enablement',
    'builtin:rum.web.xhr-exclusion',
    'builtin:synthetic.browser.assigned-applications',
    'builtin:sessionreplay.web.resource-capturing',
    'builtin:synthetic.browser.kpms',
    'builtin:ibmmq.ims-bridges',
    'builtin:anomaly-detection.rum-mobile-crash-rate-increase',
    'builtin:disk.analytics.extension',
    'builtin:cloud.cloudfoundry',
    'builtin:anomaly-detection.infrastructure-disks.per-disk-override',
    'builtin:synthetic.browser.scheduling',
    'builtin:synthetic.http.assigned-applications',
    'builtin:anomaly-detection.disk-rules',
    'builtin:rum.custom.enablement',
    'ext:com.dynatrace.extension.palo-alto-generic',
    'builtin:synthetic.http.cookies',
    'builtin:processavailability',
    'builtin:rum.custom.name'
]


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    summary.append('Settings 2.0 schemas with objects defined (that differ from known defaults):')

    endpoint = '/api/v2/settings/schemas'
    params = ''
    settings_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)

    if print_mode:
        print('schemaId' + '|' + 'displayName' + '|' + 'latestSchemaVersion')

    for settings_json in settings_json_list:
        inner_settings_json_list = settings_json.get('items')
        for inner_settings_json in inner_settings_json_list:
            schema_id = inner_settings_json.get('schemaId')
            display_name = inner_settings_json.get('displayName')
            latest_schema_version = inner_settings_json.get('latestSchemaVersion')

            if print_mode:
                print(schema_id + '|' + display_name + '|' + latest_schema_version)

            endpoint = '/api/v2/settings/objects'
            raw_params = f'schemaIds={schema_id}&scopes=environment&fields=objectId,value&pageSize=500'
            params = urllib.parse.quote(raw_params, safe='/,&=')
            object = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]
            items = object.get('items')
            count_objects = 0
            for item in items:
                objectId = item.get('objectId')
                value = str(item.get('value'))
                value = value.replace('{', '')
                value = value.replace('}', '')
                value = value.replace("'", "")
                if print_mode:
                    print(value + ' - ' + objectId)
                count_objects += 1

            if print_mode:
                print('Total ' + schema_id + ' Objects: ' + str(count_objects))

            if count_objects > 0 and content_differs_from_default_values(schema_id, items, print_mode):
                summary.append('Total ' + schema_id + ' Objects: ' + str(count_objects))

            if print_mode:
                if count_objects == 0 and schema_defaults.get(schema_id,
                                                              'NOTFOUND') == 'NOTFOUND' and schema_id not in schema_expected_empty:
                    print('add to expected empty list: ' + schema_id)

            count_total += 1

    # It just happens that the whole summary can be sorted in this particular case.
    summary = sorted(summary)

    if print_mode:
        print('Total Schemas: ' + str(count_total))
        print('')
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def content_differs_from_default_values(schema_id, items, print_mode):
    defaults = schema_defaults.get(schema_id, [])
    return values_differ_from_defaults(schema_id, items, defaults, print_mode)


def values_differ_from_defaults(schema_id, items, defaults, print_mode):
    values = []
    for item in items:
        values.append(str(item.get('value')))

    if print_mode:
        if defaults == [] and schema_id not in schema_expected_empty:
            print('You may need to add the following entry to schema_defaults dictionary: ')
            print("'" + schema_id + "': " + str(values) + ",")

    # DEBUG: TURN ON TO LOOK FOR CHANGES TO DEFAULTS
    if print_mode:
        print('values vs. defaults:')
        print(values)
        print(defaults)
    if sorted(values) != sorted(defaults):
        # print('values != defaults')
        return True
    else:
        # print('values == defaults')
        return False


def main():
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, True)


if __name__ == '__main__':
    # print('Not to be run standalone.  Use one of the "perform_*.py" modules to run this module.')
    # exit(1)
    main()
