from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []

    endpoint = '/api/config/v1/anomalyDetection/services'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    anomaly_json = r.json()

    default_response_time_degradation_detection_mode = 'DETECT_AUTOMATICALLY'
    default_response_time_degradation_milliseconds = 100
    default_response_time_degradation_percent = 50
    default_slowest_response_time_degradation_milliseconds = 1000
    default_slowest_response_time_degradation_percent = 100
    default_response_time_degradation_load_threshold = 'TEN_REQUESTS_PER_MINUTE'
    default_load_drop_enabled = False
    default_load_spike_enabled = False
    default_failure_rate_increase_detection_mode = 'DETECT_AUTOMATICALLY'
    default_failing_service_call_percentage_increase_absolute = 0
    default_failing_service_call_percentage_increase_relative = 50

    response_time_degradation = anomaly_json.get('responseTimeDegradation')
    load_drop = anomaly_json.get('loadDrop')
    load_spike = anomaly_json.get('loadSpike')
    failure_rate_increase = anomaly_json.get('failureRateIncrease')

    response_time_degradation_detection_mode = response_time_degradation.get('detectionMode')

    if response_time_degradation_detection_mode == 'DETECT_AUTOMATICALLY':
        response_time_degradation_automatic_detection = response_time_degradation.get('automaticDetection')
        response_time_degradation_milliseconds = response_time_degradation_automatic_detection.get('responseTimeDegradationMilliseconds')
        response_time_degradation_percent = response_time_degradation_automatic_detection.get('responseTimeDegradationPercent')
        slowest_response_time_degradation_milliseconds = response_time_degradation_automatic_detection.get('slowestResponseTimeDegradationMilliseconds')
        slowest_response_time_degradation_percent = response_time_degradation_automatic_detection.get('slowestResponseTimeDegradationPercent')
        response_time_degradation_load_threshold = response_time_degradation_automatic_detection.get('loadThreshold')
        response_time_degradation_or_threshold_milliseconds = response_time_degradation_milliseconds
        response_time_degradation_or_threshold_percent = response_time_degradation_percent
        slowest_response_time_degradation_or_threshold_milliseconds = slowest_response_time_degradation_milliseconds
        slowest_response_time_degradation_or_threshold_percent = slowest_response_time_degradation_percent
        response_time_degradation_or_threshold_milliseconds_label = 'Response Time Degradation Milliseconds'
        response_time_degradation_or_threshold_percent_label = 'Response Time Degradation Percent'
        slowest_response_time_degradation_or_threshold_milliseconds_label = 'Slowest Response Time Degradation Milliseconds'
        slowest_response_time_degradation_or_threshold_percent_label = 'Slowest Response Time Degradation Percent'
    else:
        response_time_degradation_thresholds_detection = response_time_degradation.get('thresholds')
        response_time_threshold_milliseconds = response_time_degradation_thresholds_detection.get('responseTimeThresholdMilliseconds')
        response_time_threshold_percent = response_time_degradation_thresholds_detection.get('responseTimeThresholdPercent')
        slowest_response_time_threshold_milliseconds = response_time_degradation_thresholds_detection.get('slowestResponseTimeThresholdMilliseconds')
        slowest_response_time_threshold_percent = response_time_degradation_thresholds_detection.get('slowestResponseTimeThresholdPercent')
        response_time_degradation_load_threshold = response_time_degradation_thresholds_detection.get('loadThreshold')
        response_time_degradation_or_threshold_milliseconds = response_time_threshold_milliseconds
        response_time_degradation_or_threshold_percent = response_time_threshold_percent
        slowest_response_time_degradation_or_threshold_milliseconds = slowest_response_time_threshold_milliseconds
        slowest_response_time_degradation_or_threshold_percent = slowest_response_time_threshold_percent
        response_time_degradation_or_threshold_milliseconds_label = 'Response Time Threshold Milliseconds'
        response_time_degradation_or_threshold_percent_label = 'Response Time Threshold Percent'
        slowest_response_time_degradation_or_threshold_milliseconds_label = 'Slowest Response Time Threshold Milliseconds'
        slowest_response_time_degradation_or_threshold_percent_label = 'Slowest Response Time Threshold Percent'

    load_drop_enabled = load_drop.get('enabled')
    load_drop_percent = load_drop.get('loadDropPercent')

    load_spike_enabled = load_spike.get('enabled')
    load_spike_percent = load_spike.get('loadSpikePercent')

    failure_rate_increase_detection_mode = failure_rate_increase.get('detectionMode')
    failure_rate_increase_automatic_detection = failure_rate_increase.get('automaticDetection')
    failing_service_call_percentage_increase_absolute = failure_rate_increase_automatic_detection.get('failingServiceCallPercentageIncreaseAbsolute')
    failing_service_call_percentage_increase_relative = failure_rate_increase_automatic_detection.get('failingServiceCallPercentageIncreaseRelative')

    # TESTING
    # response_time_degradation_detection_mode = 'WACKY_VALUE'
    # response_time_degradation_milliseconds = 999
    # response_time_degradation_percent = 99
    # slowest_response_time_degradation_milliseconds = 9999
    # slowest_response_time_degradation_percent = 999
    # response_time_degradation_load_threshold = 'WACKY_VALUE_2'
    # load_drop_enabled = True
    # load_spike_enabled = True
    # failure_rate_increase_detection_mode = 'WACKY_VALUE_3'
    # failing_service_call_percentage_increase_absolute = 9
    # failing_service_call_percentage_increase_relative = 99

    if not summary_mode:
        rows.append(('Response Time Degradation Detection Mode', response_time_degradation_detection_mode))
        rows.append((response_time_degradation_or_threshold_milliseconds_label, response_time_degradation_or_threshold_milliseconds))
        rows.append((response_time_degradation_or_threshold_percent_label, response_time_degradation_or_threshold_percent))
        rows.append((slowest_response_time_degradation_or_threshold_milliseconds_label, slowest_response_time_degradation_or_threshold_milliseconds))
        rows.append((slowest_response_time_degradation_or_threshold_percent_label, slowest_response_time_degradation_or_threshold_percent))
        rows.append(('Response Time Degradation Load Threshold', response_time_degradation_load_threshold))
        rows.append(('Traffic Drop Enabled', str(load_drop_enabled)))
        rows.append(('Traffic Drop Percent', load_drop_percent))
        rows.append(('Traffic Spike Enabled', str(load_spike_enabled)))
        rows.append(('Traffic Spike Percent', load_spike_percent))
        rows.append(('Failure Rate Increase Detection Mode', failure_rate_increase_detection_mode))
        rows.append(('Failing Service Call Percentage Increase Absolute', failing_service_call_percentage_increase_absolute))
        rows.append(('Failing Service Call Percentage Increase Relative', failing_service_call_percentage_increase_relative))

    if response_time_degradation_detection_mode == default_response_time_degradation_detection_mode and \
        response_time_degradation_or_threshold_milliseconds == default_response_time_degradation_milliseconds and \
        response_time_degradation_or_threshold_percent == default_response_time_degradation_percent and \
        slowest_response_time_degradation_or_threshold_milliseconds == default_slowest_response_time_degradation_milliseconds and \
        slowest_response_time_degradation_or_threshold_percent == default_slowest_response_time_degradation_percent and \
        response_time_degradation_load_threshold == default_response_time_degradation_load_threshold and \
        load_drop_enabled == default_load_drop_enabled and \
        load_spike_enabled == default_load_spike_enabled and \
        failure_rate_increase_detection_mode == default_failure_rate_increase_detection_mode and \
        failing_service_call_percentage_increase_absolute == default_failing_service_call_percentage_increase_absolute and \
            failing_service_call_percentage_increase_relative == default_failing_service_call_percentage_increase_relative:
        summary.append('Anomaly detection settings for services have not been modified.')
    else:
        summary.append('Anomaly detection settings for services have been modified.' + '')
        summary.append('Differences:')
        if response_time_degradation_detection_mode != default_response_time_degradation_detection_mode:
            summary.append('detectionMode:                                ' + response_time_degradation_detection_mode + ' (vs. default of ' + default_response_time_degradation_detection_mode + ')')
        if response_time_degradation_or_threshold_milliseconds != default_response_time_degradation_milliseconds:
            summary.append('responseTimeDegradationMilliseconds:          ' + str(response_time_degradation_or_threshold_milliseconds) + ' (vs. default of ' + str(default_response_time_degradation_milliseconds) + ')')
        if response_time_degradation_or_threshold_percent != default_response_time_degradation_percent:
            summary.append('responseTimeDegradationPercent:               ' + str(response_time_degradation_or_threshold_percent) + ' (vs. default of ' + str(default_response_time_degradation_percent) + ')')
        if slowest_response_time_degradation_or_threshold_milliseconds != default_slowest_response_time_degradation_milliseconds:
            summary.append('slowestResponseTimeDegradationMilliseconds:   ' + str(slowest_response_time_degradation_or_threshold_milliseconds) + ' (vs. default of ' + str(default_slowest_response_time_degradation_milliseconds) + ')')
        if slowest_response_time_degradation_or_threshold_percent != default_slowest_response_time_degradation_percent:
            summary.append('slowestResponseTimeDegradationPercent:        ' + str(slowest_response_time_degradation_or_threshold_percent) + ' (vs. default of ' + str(default_slowest_response_time_degradation_percent) + ')')
        if response_time_degradation_load_threshold != default_response_time_degradation_load_threshold:
            summary.append('loadThreshold:                                ' + response_time_degradation_load_threshold + ' (vs. default of ' + str(default_response_time_degradation_load_threshold) + ')')
        if load_drop_enabled != default_load_drop_enabled:
            summary.append('enabled:                                      ' + str(load_drop_enabled) + ' (vs. default of ' + str(default_load_drop_enabled) + ')')
        if load_spike_enabled != default_load_spike_enabled:
            summary.append('enabled:                                      ' + str(load_spike_enabled) + ' (vs. default of ' + str(default_load_spike_enabled) + ')')
        if failure_rate_increase_detection_mode != default_failure_rate_increase_detection_mode:
            summary.append('detectionMode:                                ' + failure_rate_increase_detection_mode + ' (vs. default of ' + default_failure_rate_increase_detection_mode + ')')
        if failing_service_call_percentage_increase_absolute != default_failing_service_call_percentage_increase_absolute:
            summary.append('failingServiceCallPercentageIncreaseAbsolute: ' + str(failing_service_call_percentage_increase_absolute) + ' (vs. default of ' + str(default_failing_service_call_percentage_increase_absolute) + ')')
        if failing_service_call_percentage_increase_relative != default_failing_service_call_percentage_increase_relative:
            summary.append('failingServiceCallPercentageIncreaseRelative: ' + str(failing_service_call_percentage_increase_relative) + ' (vs. default of ' + str(default_failing_service_call_percentage_increase_relative) + ')')

    if not summary_mode:
        report_name = 'Service Anomaly Detection'
        report_writer.initialize_text_file(None)
        report_headers = ['Setting', 'Value']
        report_writer.write_console(report_name, report_headers, rows, delimiter=': ')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter=': ')
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def convert_boolean(boolean):
    if boolean:
        return 'on'
    else:
        return'off'
        

def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
