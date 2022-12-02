import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    endpoint = '/api/config/v1/anomalyDetection/hosts'
    params = ''
    anomaly_json = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]

    default_connection_lost_detection = True
    default_connection_lost_detection_on_graceful_shutdowns = False
    default_high_cpu_saturation_detection = True
    default_high_memory_detection = True
    default_high_gc_activity_detection = True
    default_out_of_memory_detection = True
    default_out_of_threads_detection = True
    default_network_dropped_packets_detection = True
    default_network_errors_detection = True
    default_high_network_detection = True
    default_network_tcp_problems_detection = True
    default_network_high_retransmission_detection = True
    default_disk_low_space_detection = True
    default_disk_slow_writes_and_reads_detection = True
    default_disk_low_inodes_detection = True

    connection_lost_detection = anomaly_json.get('connectionLostDetection').get('enabled')
    connection_lost_detection_on_graceful_shutdowns = anomaly_json.get('connectionLostDetection').get('enabledOnGracefulShutdowns')
    high_cpu_saturation_detection = anomaly_json.get('highCpuSaturationDetection').get('enabled')
    high_memory_detection = anomaly_json.get('highMemoryDetection').get('enabled')
    high_gc_activity_detection = anomaly_json.get('highGcActivityDetection').get('enabled')
    out_of_memory_detection = anomaly_json.get('outOfMemoryDetection').get('enabled')
    out_of_threads_detection = anomaly_json.get('outOfThreadsDetection').get('enabled')
    network_dropped_packets_detection = anomaly_json.get('networkDroppedPacketsDetection').get('enabled')
    network_errors_detection = anomaly_json.get('networkErrorsDetection').get('enabled')
    high_network_detection = anomaly_json.get('highNetworkDetection').get('enabled')
    network_tcp_problems_detection = anomaly_json.get('networkTcpProblemsDetection').get('enabled')
    network_high_retransmission_detection = anomaly_json.get('networkHighRetransmissionDetection').get('enabled')
    disk_low_space_detection = anomaly_json.get('diskLowSpaceDetection').get('enabled')
    disk_slow_writes_and_reads_detection = anomaly_json.get('diskSlowWritesAndReadsDetection').get('enabled')
    disk_low_inodes_detection = anomaly_json.get('diskLowInodesDetection').get('enabled')

    # TESTING
    # connection_lost_detection = False
    # connection_lost_detection_on_graceful_shutdowns = True
    # high_cpu_saturation_detection = False
    # high_memory_detection = False
    # high_gc_activity_detection = False
    # out_of_memory_detection = False
    # out_of_threads_detection = False
    # network_dropped_packets_detection = False
    # network_errors_detection = False
    # high_network_detection = False
    # network_tcp_problems_detection = True
    # network_high_retransmission_detection = False
    # disk_low_space_detection = False
    # disk_slow_writes_and_reads_detection = False
    # disk_low_inodes_detection = False

    if print_mode:
        print('connectionLostDetection:                      ' + str(connection_lost_detection))
        print('connectionLostDetectionOnGracefulShutdowns:   ' + str(connection_lost_detection_on_graceful_shutdowns))
        print('highCpuSaturationDetection:                   ' + str(high_cpu_saturation_detection))
        print('highMemoryDetection:                          ' + str(high_memory_detection))
        print('highGcActivityDetection:                      ' + str(high_gc_activity_detection))
        print('outOfMemoryDetection:                         ' + str(out_of_memory_detection))
        print('outOfThreadsDetection:                        ' + str(out_of_threads_detection))
        print('networkDroppedPacketsDetection:               ' + str(network_dropped_packets_detection))
        print('networkErrorsDetection:                       ' + str(network_errors_detection))
        print('highNetworkDetection:                         ' + str(high_network_detection))
        print('networkTcpProblemsDetection:                  ' + str(network_tcp_problems_detection))
        print('networkHighRetransmissionDetection:           ' + str(network_high_retransmission_detection))
        print('diskLowSpaceDetection:                        ' + str(disk_low_space_detection))
        print('diskSlowWritesAndReadsDetection:              ' + str(disk_slow_writes_and_reads_detection))
        print('diskLowInodesDetection:                       ' + str(disk_low_inodes_detection))

    if connection_lost_detection == default_connection_lost_detection and \
        connection_lost_detection_on_graceful_shutdowns == default_connection_lost_detection_on_graceful_shutdowns and \
        high_cpu_saturation_detection == default_high_cpu_saturation_detection and \
        high_memory_detection == default_high_memory_detection and \
        high_gc_activity_detection == default_high_gc_activity_detection and \
        out_of_memory_detection == default_out_of_memory_detection and \
        out_of_threads_detection == default_out_of_threads_detection and \
        network_dropped_packets_detection == default_network_dropped_packets_detection and \
        network_errors_detection == default_network_errors_detection and \
        high_network_detection == default_high_network_detection and \
        network_tcp_problems_detection == default_network_tcp_problems_detection and \
        network_high_retransmission_detection == default_network_high_retransmission_detection and \
        disk_low_space_detection == default_disk_low_space_detection and \
        disk_slow_writes_and_reads_detection == default_disk_slow_writes_and_reads_detection and \
        disk_low_inodes_detection == default_disk_low_inodes_detection:
        summary.append('Anomaly detection settings for hosts have not been modified.')
    else:
        summary.append('Anomaly detection settings for hosts have been modified.')
        summary.append('Differences:')
        if connection_lost_detection != default_connection_lost_detection:
            summary.append('connectionLostDetection:                    ' + str(connection_lost_detection) + ' (vs. default of ' + str(default_connection_lost_detection) + ')')
        if connection_lost_detection_on_graceful_shutdowns != default_connection_lost_detection_on_graceful_shutdowns:
            summary.append('connectionLostDetectionOnGracefulShutdowns: ' + str(connection_lost_detection_on_graceful_shutdowns) + ' (vs. default of ' + str(default_connection_lost_detection_on_graceful_shutdowns) + ')')
        if high_cpu_saturation_detection != default_high_cpu_saturation_detection:
            summary.append('highCpuSaturationDetection:                 ' + str(high_cpu_saturation_detection) + ' (vs. default of ' + str(default_high_cpu_saturation_detection) + ')')
        if high_memory_detection != default_high_memory_detection:
            summary.append('highMemoryDetection:                        ' + str(high_memory_detection) + ' (vs. default of ' + str(default_high_memory_detection) + ')')
        if high_gc_activity_detection != default_high_gc_activity_detection:
            summary.append('highGcActivityDetection:                    ' + str(high_gc_activity_detection) + ' (vs. default of ' + str(default_high_gc_activity_detection) + ')')
        if out_of_memory_detection != default_out_of_memory_detection:
            summary.append('outOfMemoryDetection:                       ' + str(out_of_memory_detection) + ' (vs. default of ' + str(default_out_of_memory_detection) + ')')
        if out_of_threads_detection != default_out_of_threads_detection:
            summary.append('outOfThreadsDetection:                      ' + str(out_of_threads_detection) + ' (vs. default of ' + str(default_out_of_threads_detection) + ')')
        if network_dropped_packets_detection != default_network_dropped_packets_detection:
            summary.append('networkDroppedPacketsDetection:             ' + str(network_dropped_packets_detection) + ' (vs. default of ' + str(default_network_dropped_packets_detection) + ')')
        if network_errors_detection != default_network_errors_detection:
            summary.append('networkErrorsDetection:                     ' + str(network_errors_detection) + ' (vs. default of ' + str(default_network_errors_detection) + ')')
        if high_network_detection != default_high_network_detection:
            summary.append('highNetworkDetection:                       ' + str(high_network_detection) + ' (vs. default of ' + str(default_high_network_detection) + ')')
        if network_tcp_problems_detection != default_network_tcp_problems_detection:
            summary.append('networkTcpProblemsDetection:                ' + str(network_tcp_problems_detection) + ' (vs. default of ' + str(default_network_tcp_problems_detection) + ')')
        if network_high_retransmission_detection != default_network_high_retransmission_detection:
            summary.append('networkHighRetransmissionDetection :        ' + str(network_high_retransmission_detection) + ' (vs. default of ' + str(default_network_high_retransmission_detection) + ')')
        if disk_low_space_detection != default_disk_low_space_detection:
            summary.append('diskLowSpaceDetection:                      ' + str(disk_low_space_detection) + ' (vs. default of ' + str(default_disk_low_space_detection) + ')')
        if disk_slow_writes_and_reads_detection != default_disk_slow_writes_and_reads_detection:
            summary.append('diskSlowWritesAndReadsDetection:            ' + str(disk_slow_writes_and_reads_detection) + ' (vs. default of ' + str(default_disk_slow_writes_and_reads_detection) + ')')
        if disk_low_inodes_detection != default_disk_low_inodes_detection:
            summary.append('diskLowInodesDetection:                     ' + str(disk_low_inodes_detection) + ' (vs. default of ' + str(default_disk_low_inodes_detection) + ')')

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
