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

    endpoint = '/api/config/v1/anomalyDetection/hosts'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    anomaly_json = r.json()


    default_connection_lost_detection = True
    default_connection_lost_detection_on_graceful_shutdowns = False
    default_high_cpu_saturation_detection = True
    default_high_memory_detection = True
    default_high_gc_activity_detection = True
    default_out_of_memory_detection = True
    default_out_of_threads_detection = True
    default_network_dropped_packets_detection = True
    default_network_errors_detection = True
    default_high_network_detection = False
    default_network_tcp_problems_detection = False
    default_network_high_retransmission_detection = False
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

    if not summary_mode:
        rows.append(('Connection Lost Detection', str(connection_lost_detection)))
        rows.append(('Connection Lost Detection on Graceful Shutdowns', str(connection_lost_detection_on_graceful_shutdowns)))
        rows.append(('High Cpu Saturation Detection', str(high_cpu_saturation_detection)))
        rows.append(('High Memory Detection', str(high_memory_detection)))
        rows.append(('High Garbage Collection Activity Detection', str(high_gc_activity_detection)))
        rows.append(('Out of Memory Detection', str(out_of_memory_detection)))
        rows.append(('Out of Threads Detection', str(out_of_threads_detection)))
        rows.append(('Network Dropped Packets Detection', str(network_dropped_packets_detection)))
        rows.append(('Network Errors Detection', str(network_errors_detection)))
        rows.append(('High Network Detection', str(high_network_detection)))
        rows.append(('Network TCP Problems Detection', str(network_tcp_problems_detection)))
        rows.append(('Network High Retransmission Detection', str(network_high_retransmission_detection)))
        rows.append(('Disk Low Space Detection', str(disk_low_space_detection)))
        rows.append(('Disk Slow Writes and Reads Detection', str(disk_slow_writes_and_reads_detection)))
        rows.append(('Disk Low Inodes Detection', str(disk_low_inodes_detection)))

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

    if not summary_mode:
        report_name = 'Host Anomaly Detection'
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
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
