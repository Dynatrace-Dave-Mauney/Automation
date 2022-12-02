import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    endpoint = '/api/config/v1/anomalyDetection/services'
    params = ''
    anomaly_json = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]

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
    response_time_degradation_automatic_detection = response_time_degradation.get('automaticDetection')
    response_time_degradation_milliseconds = response_time_degradation_automatic_detection.get('responseTimeDegradationMilliseconds')
    response_time_degradation_percent = response_time_degradation_automatic_detection.get('responseTimeDegradationPercent')
    slowest_response_time_degradation_milliseconds = response_time_degradation_automatic_detection.get('slowestResponseTimeDegradationMilliseconds')
    slowest_response_time_degradation_percent = response_time_degradation_automatic_detection.get('slowestResponseTimeDegradationPercent')
    response_time_degradation_load_threshold = response_time_degradation_automatic_detection.get('loadThreshold')

    load_drop_enabled = load_drop.get('enabled')

    load_spike_enabled = load_spike.get('enabled')

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

    if print_mode:
        print('Response Time Degradation Settings:')
        print('detectionMode:                                ' + response_time_degradation_detection_mode)
        print('responseTimeDegradationMilliseconds:          ' + str(response_time_degradation_milliseconds))
        print('responseTimeDegradationPercent:               ' + str(response_time_degradation_percent))
        print('slowestResponseTimeDegradationMilliseconds:   ' + str(slowest_response_time_degradation_milliseconds))
        print('slowestResponseTimeDegradationPercent:        ' + str(slowest_response_time_degradation_percent))
        print('loadThreshold:                                ' + response_time_degradation_load_threshold)

        print('load Drop Settings:')
        print('enabled:                                      ' + str(load_drop_enabled))

        print('load Spike Settings:')
        print('enabled:                                      ' + str(load_spike_enabled))

        print('Failure Rate Increase Settings:')
        print('detectionMode:                                ' + failure_rate_increase_detection_mode)
        print('failingServiceCallPercentageIncreaseAbsolute: ' + str(failing_service_call_percentage_increase_absolute))
        print('failingServiceCallPercentageIncreaseRelative: ' + str(failing_service_call_percentage_increase_relative))

    if response_time_degradation_detection_mode == default_response_time_degradation_detection_mode and \
        response_time_degradation_milliseconds == default_response_time_degradation_milliseconds and \
        response_time_degradation_percent == default_response_time_degradation_percent and \
        slowest_response_time_degradation_milliseconds == default_slowest_response_time_degradation_milliseconds and \
        slowest_response_time_degradation_percent == default_slowest_response_time_degradation_percent and \
        response_time_degradation_load_threshold == default_response_time_degradation_load_threshold and \
        load_drop_enabled == default_load_drop_enabled and \
        load_spike_enabled == default_load_spike_enabled and \
        failure_rate_increase_detection_mode == default_failure_rate_increase_detection_mode and \
        failing_service_call_percentage_increase_absolute == default_failing_service_call_percentage_increase_absolute and \
        failing_service_call_percentage_increase_relative == default_failing_service_call_percentage_increase_relative:
        summary.append('Anomaly detection settings for services have not been modified.')
    else:
        summary.append('Anomaly detection settings for services have been modified.')
        summary.append('Differences:')
        if response_time_degradation_detection_mode != default_response_time_degradation_detection_mode:
            summary.append('detectionMode:                                ' + response_time_degradation_detection_mode + ' (vs. default of ' + default_response_time_degradation_detection_mode + ')')
        if response_time_degradation_milliseconds != default_response_time_degradation_milliseconds:
            summary.append('responseTimeDegradationMilliseconds:          ' + str(response_time_degradation_milliseconds) + ' (vs. default of ' + str(default_response_time_degradation_milliseconds) + ')')
        if response_time_degradation_percent != default_response_time_degradation_percent:
            summary.append('responseTimeDegradationPercent:               ' + str(response_time_degradation_percent) + ' (vs. default of ' + str(default_response_time_degradation_percent) + ')')
        if slowest_response_time_degradation_milliseconds != default_slowest_response_time_degradation_milliseconds:
            summary.append('slowestResponseTimeDegradationMilliseconds:   ' + str(slowest_response_time_degradation_milliseconds) + ' (vs. default of ' + str(default_slowest_response_time_degradation_milliseconds) + ')')
        if slowest_response_time_degradation_percent != default_slowest_response_time_degradation_percent:
            summary.append('slowestResponseTimeDegradationPercent:        ' + str(slowest_response_time_degradation_percent) + ' (vs. default of ' + str(default_slowest_response_time_degradation_percent) + ')')
        if response_time_degradation_load_threshold != default_response_time_degradation_load_threshold:
            summary.append('loadThreshold:                                ' + str(response_time_degradation_load_threshold) + ' (vs. default of ' + str(default_response_time_degradation_load_threshold) + ')')
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

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def convert_boolean(boolean):
    if boolean:
        return 'on'
    else:
        return'off'
        

def main():
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, True)


if __name__ == '__main__':
    # print('Not to be run standalone.  Use one of the "perform_*.py" modules to run this module.')
    # exit(1)
    main()
