import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


expected_rum_host_headers = ['Host', 'X-Forwarded-Host', 'X-Host']
rum_host_headers = []
expected_rum_ip_determination = ['CF-Connecting-IP', 'True-Client-IP', 'X-Client-Ip', 'X-Cluster-Client-Ip', 'X-Forwarded-For', 'X-Http-Client-Ip', 'rproxy_remote_address']
rum_ip_determination = []
rum_ip_mappings_added = False

ignore_list = [
    'builtin:alerting.profile',
    'builtin:apis.detection-rules',
    'builtin:container.monitoring-rule',
    'builtin:container.technology',
    'builtin:dashboards.general',
    'builtin:dashboards.presets',
    'builtin:deployment.management.update-windows',
    'builtin:elasticsearch.user-session-export-settings-v2',
    'builtin:eula-settings',
    'builtin:logmonitoring.log-dpp-rules',
    'builtin:logmonitoring.log-events',
    'builtin:mainframe.mqfilters',
    'builtin:mainframe.txmonitoring',
    'builtin:mainframe.txstartfilters',
    'builtin:monitoredentities.generic.relation',
    'builtin:monitoredentities.generic.type',
    'builtin:monitoring.slo',
    'builtin:oneagent.features',
    'builtin:os-services-monitoring',
    'builtin:problem.notifications',
    'builtin:process-group.cloud-application-workload-detection',
    'builtin:process-group.detection-flags',
    'builtin:process.built-in-process-monitoring-rule',
    'builtin:resource-attribute',
    'builtin:span-attribute',
    'builtin:span-entry-points',
    'builtin:span-event-attribute',
    'builtin:tags.auto-tagging'
]


def summarize(env, token):
    return process(env, token, False)


def process_environment_scope(env, token, print_mode):
    summary = []
    findings = []

    # summary.append('Interesting Settings 2.0 schemas with objects defined:')

    endpoint = '/api/v2/settings/objects'
    raw_params = 'scopes=environment&fields=schemaId,value&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object = dynatrace_api.get(env, token, endpoint, params)[0]
    items = settings_object.get('items')
    for item in items:
        schema_id = item.get('schemaId')
        value = str(item.get('value'))
        value = value.replace('{', '')
        value = value.replace('}', '')
        value = value.replace("'", "")
        if print_mode:
            if schema_id not in ignore_list:
                print(schema_id + ': ' + value)

        add_findings(findings, schema_id, item)

    # It just happens that the whole summary can be sorted in this particular case.
    summary = sorted(summary)

    add_findings_based_on_lists(findings)
    add_findings_based_on_booleans(findings)

    if len(findings) > 0:
        summary.append('Environment findings:')
        summary.extend(findings)
    else:
        summary.append('Environment has no findings')

    if print_mode:
        print_list(summary)
        print('Environment Scope Done!')

    return summary


def add_findings(findings, schema_id, item):
    value = item.get('value')

    if schema_id == 'builtin:audit-log':
        if value.get('enabled') is not True:
            findings.append('Audit logging is disabled.')
        return

    if schema_id == 'builtin:networkzones':
        if value.get('enabled') is not True:
            findings.append('Network zones are disabled.')
        return

    if schema_id == 'builtin:anomaly-detection.frequent-issues':
        if value.get('detectFrequentIssuesInApplications') and \
            value.get('detectFrequentIssuesInTransactionsAndServices') and \
            value.get('detectFrequentIssuesInInfrastructure'):
            pass
        else:
            findings.append('Frequent issue detection has been modified.')
        return

    # TODO: Figure out best way to handle differences of more complex schemas (list at bottom of source code)
    # if schema_id == 'builtin:anomaly-detection.databases':
    # 	print(str(item))
    # 	exit()
    # 	# 'responseTime: enabled: True, detectionMode: auto, autoDetection: responseTimeAll: degradationMilliseconds: 5.0, degradationPercent: 50.0, responseTimeSlowest: slowestDegradationMilliseconds: 20.0, slowestDegradationPercent: 100.0, overAlertingProtection: requestsPerMinute: 10.0, minutesAbnormalState: 1, failureRate: enabled: True, detectionMode: auto, autoDetection: absoluteIncrease: 0.0, relativeIncrease: 50.0, overAlertingProtection: requestsPerMinute: 10.0, minutesAbnormalState: 1, loadDrops: enabled: False, loadSpikes: enabled: False, databaseConnections: enabled: True, maxFailedConnects: 5, timePeriod: 5'

    # Schemas that need to be saved for later processing
    if schema_id == 'builtin:rum.ip-mappings':
        global rum_ip_mappings_added
        rum_ip_mappings_added = True
        return

    if schema_id == 'builtin:rum.host-headers':
        global rum_host_headers
        rum_host_headers.append(value.get('headerName'))
        return

    if schema_id == 'builtin:rum.ip-determination':
        global rum_ip_determination
        rum_ip_determination.append(value.get('headerName'))
        return


def add_findings_based_on_lists(findings):
    sorted_rum_host_headers = sorted(rum_host_headers)
    if sorted_rum_host_headers != expected_rum_host_headers:
        findings.append('Host headers have been modified:')
        findings.append('Expected: ' + str(expected_rum_host_headers))
        findings.append('Actual: ' + str(sorted_rum_host_headers))

    sorted_rum_ip_determination = sorted(rum_ip_determination)
    if sorted_rum_ip_determination != expected_rum_ip_determination:
        findings.append('Host ip determination headers have been modified:')
        findings.append('Expected: ' + str(expected_rum_ip_determination))
        findings.append('Actual: ' + str(sorted_rum_ip_determination))


def add_findings_based_on_booleans(findings):
    if rum_ip_mappings_added:
        findings.append('RUM IP mappings have been added.')


def process(env, token, print_mode):
    return process_environment_scope(env, token, print_mode)


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token, True)
    
    
if __name__ == '__main__':
    main()

# TODO: Figure out best way to handle differences of more complex schemas:
'''
builtin:anomaly-detection.databases: responseTime: enabled: True, detectionMode: auto, autoDetection: responseTimeAll: degradationMilliseconds: 5.0, degradationPercent: 50.0, responseTimeSlowest: slowestDegradationMilliseconds: 20.0, slowestDegradationPercent: 100.0, overAlertingProtection: requestsPerMinute: 10.0, minutesAbnormalState: 1, failureRate: enabled: True, detectionMode: auto, autoDetection: absoluteIncrease: 0.0, relativeIncrease: 50.0, overAlertingProtection: requestsPerMinute: 10.0, minutesAbnormalState: 1, loadDrops: enabled: False, loadSpikes: enabled: False, databaseConnections: enabled: True, maxFailedConnects: 5, timePeriod: 5
builtin:anomaly-detection.frequent-issues: detectFrequentIssuesInApplications: True, detectFrequentIssuesInTransactionsAndServices: True, detectFrequentIssuesInInfrastructure: True
builtin:anomaly-detection.infrastructure-aws: ec2CandidateHighCpuDetection: enabled: True, detectionMode: auto, rdsHighCpuDetection: enabled: True, detectionMode: auto, rdsHighWriteReadLatencyDetection: enabled: True, detectionMode: auto, rdsLowStorageDetection: enabled: True, detectionMode: auto, rdsHighMemoryDetection: enabled: True, detectionMode: auto, elbHighConnectionErrorsDetection: enabled: True, detectionMode: auto, rdsRestartsSequenceDetection: enabled: True, detectionMode: auto, lambdaHighErrorRateDetection: enabled: True, detectionMode: auto
builtin:anomaly-detection.infrastructure-disks: disk: diskLowSpaceDetection: enabled: True, detectionMode: auto, diskSlowWritesAndReadsDetection: enabled: True, detectionMode: auto, diskLowInodesDetection: enabled: True, detectionMode: auto
builtin:anomaly-detection.infrastructure-hosts: host: connectionLostDetection: enabled: True, onGracefulShutdowns: DONT_ALERT_ON_GRACEFUL_SHUTDOWN, highCpuSaturationDetection: enabled: True, detectionMode: auto, highMemoryDetection: enabled: True, detectionMode: auto, highGcActivityDetection: enabled: True, detectionMode: auto, outOfMemoryDetection: enabled: True, detectionMode: auto, outOfThreadsDetection: enabled: True, detectionMode: auto, network: networkDroppedPacketsDetection: enabled: True, detectionMode: auto, networkErrorsDetection: enabled: True, detectionMode: auto, highNetworkDetection: enabled: True, detectionMode: auto, networkTcpProblemsDetection: enabled: True, detectionMode: auto, networkHighRetransmissionDetection: enabled: True, detectionMode: auto
builtin:anomaly-detection.infrastructure-vmware: esxiHighCpuDetection: enabled: True, detectionMode: auto, guestCpuLimitDetection: enabled: True, detectionMode: auto, esxiHighMemoryDetection: enabled: True, detectionMode: auto, overloadedStorageDetection: enabled: True, detectionMode: auto, undersizedStorageDetection: enabled: True, detectionMode: auto, slowPhysicalStorageDetection: enabled: True, detectionMode: auto, droppedPacketsDetection: enabled: True, detectionMode: auto, lowDatastoreSpaceDetection: enabled: True, detectionMode: auto
builtin:anomaly-detection.rum-custom: errorRateIncrease: enabled: True, detectionMode: auto, errorRateIncreaseAuto: thresholdAbsolute: 5.0, thresholdRelative: 50.0, slowUserActions: enabled: True, detectionMode: auto, slowUserActionsAuto: durationThresholdAll: durationThreshold: 100.0, slowdownPercentage: 50.0, durationThresholdSlowest: durationThreshold: 1000.0, slowdownPercentage: 100.0, durationAvoidOveralerting: minActionRate: 10, unexpectedLowLoad: enabled: True, thresholdPercentage: 50.0, unexpectedHighLoad: enabled: False
builtin:anomaly-detection.rum-custom-crash-rate-increase: crashRateIncrease: enabled: True, detectionMode: auto, crashRateIncreaseAuto: baselineViolationPercentage: 150.0, concurrentUsers: 5.0, sensitivity: low
builtin:anomaly-detection.rum-web: responseTime: enabled: True, detectionMode: auto, responseTimeAuto: responseTimeAll: degradationMilliseconds: 100.0, degradationPercent: 50.0, responseTimeSlowest: slowestDegradationMilliseconds: 1000.0, slowestDegradationPercent: 100.0, overAlertingProtection: actionsPerMinute: 10.0, minutesAbnormalState: 1.0, errorRate: enabled: True, errorRateDetectionMode: auto, errorRateAuto: absoluteIncrease: 5.0, relativeIncrease: 50.0, overAlertingProtection: actionsPerMinute: 10.0, minutesAbnormalState: 1.0, trafficDrops: enabled: True, trafficDrops: trafficDropPercentage: 50.0, abnormalStateAbnormalState: 1.0, trafficSpikes: enabled: False
builtin:anomaly-detection.services: responseTime: enabled: True, detectionMode: auto, autoDetection: responseTimeAll: degradationMilliseconds: 100.0, degradationPercent: 50.0, responseTimeSlowest: slowestDegradationMilliseconds: 1000.0, slowestDegradationPercent: 100.0, overAlertingProtection: requestsPerMinute: 10.0, minutesAbnormalState: 1, failureRate: enabled: True, detectionMode: auto, autoDetection: absoluteIncrease: 0.0, relativeIncrease: 50.0, overAlertingProtection: requestsPerMinute: 10.0, minutesAbnormalState: 1, loadDrops: enabled: False, loadSpikes: enabled: False
builtin:preferences.privacy: masking: ipAddressMaskingEnabled: False, personalDataUriMaskingEnabled: False, userActionMaskingEnabled: False, userTracking: persistentCookieEnabled: False, dataCollection: optInModeEnabled: False, doNotTrack: complyWithDoNotTrack: True, doNotTrack: anonymous
builtin:rum.overload-prevention: overloadPreventionLimit: 3500
builtin:rum.user-experience-score: considerLastAction: True, considerRageClick: True, maxFrustratedUserActionsThreshold: 30, minSatisfiedUserActionsThreshold: 50
builtin:sessionreplay.web.privacy-preferences: enableOptInMode: False, urlExclusionPatternList: [], maskingPresets: recordingMaskingPreset: MASK_USER_INPUT, playbackMaskingPreset: MASK_USER_INPUT
builtin:tokens.token-settings: newDynatraceTokenFormatEnabled: True, patEnabled: False
'''