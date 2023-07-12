from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    endpoint = '/api/config/v1/anomalyDetection/vmware'
    params = ''
    anomaly_json = dynatrace_api.get(env, token, endpoint, params)[0]

    default_esxi_high_cpu_saturation = True
    default_guest_cpu_limit_reached = True
    default_esxi_high_memory_detection = True
    default_overloaded_storage_detection = True
    default_undersized_storage_detection = True
    default_slow_physical_storage_detection = True
    default_dropped_packets_detection = True
    default_low_datastore_space_detection = True

    esxi_high_cpu_saturation = anomaly_json.get('esxiHighCpuSaturation').get('enabled')
    guest_cpu_limit_reached = anomaly_json.get('guestCpuLimitReached').get('enabled')
    esxi_high_memory_detection = anomaly_json.get('esxiHighMemoryDetection').get('enabled')
    overloaded_storage_detection = anomaly_json.get('overloadedStorageDetection').get('enabled')
    undersized_storage_detection = anomaly_json.get('undersizedStorageDetection').get('enabled')
    slow_physical_storage_detection = anomaly_json.get('slowPhysicalStorageDetection').get('enabled')
    dropped_packets_detection = anomaly_json.get('droppedPacketsDetection').get('enabled')
    low_datastore_space_detection = anomaly_json.get('lowDatastoreSpaceDetection').get('enabled')

    # TESTING
    # esxi_high_cpu_saturation = False
    # guest_cpu_limit_reached = False
    # esxi_high_memory_detection = False
    # overloaded_storage_detection = False
    # undersized_storage_detection = False
    # slow_physical_storage_detection = False
    # dropped_packets_detection = False
    # low_datastore_space_detection = False

    if print_mode:
        print('VMWare Anomaly Detection Settings:')
        print('esxiHighCpuSaturation:        ' + str(esxi_high_cpu_saturation))
        print('guestCpuLimitReached:         ' + str(guest_cpu_limit_reached))
        print('esxiHighMemoryDetection:      ' + str(esxi_high_memory_detection))
        print('overloadedStorageDetection:   ' + str(overloaded_storage_detection))
        print('undersizedStorageDetection:   ' + str(undersized_storage_detection))
        print('slowPhysicalStorageDetection: ' + str(slow_physical_storage_detection))
        print('droppedPacketsDetection:      ' + str(dropped_packets_detection))
        print('lowDatastoreSpaceDetection:   ' + str(low_datastore_space_detection))

    if esxi_high_cpu_saturation == default_esxi_high_cpu_saturation and \
        guest_cpu_limit_reached == default_guest_cpu_limit_reached and \
        esxi_high_memory_detection == default_esxi_high_memory_detection and \
        overloaded_storage_detection == default_overloaded_storage_detection and \
        undersized_storage_detection == default_undersized_storage_detection and \
        slow_physical_storage_detection == default_slow_physical_storage_detection and \
        dropped_packets_detection == default_dropped_packets_detection and \
        low_datastore_space_detection == default_low_datastore_space_detection:
        summary.append('Anomaly detection settings for vmware have not been modified.')
    else:
        summary.append('Anomaly detection settings for vmware have been modified.')
        summary.append('Differences:')
        if esxi_high_cpu_saturation != default_esxi_high_cpu_saturation:
            summary.append('esxiHighCpuSaturation:        ' + str(esxi_high_cpu_saturation) + ' (vs. default of ' + str(default_esxi_high_cpu_saturation) + ')')
        if guest_cpu_limit_reached != default_guest_cpu_limit_reached:
            summary.append('guestCpuLimitReached:         ' + str(guest_cpu_limit_reached) + ' (vs. default of ' + str(default_guest_cpu_limit_reached) + ')')
        if esxi_high_memory_detection != default_esxi_high_memory_detection:
            summary.append('esxiHighMemoryDetection:      ' + str(esxi_high_memory_detection) + ' (vs. default of ' + str(default_esxi_high_memory_detection) + ')')
        if overloaded_storage_detection != default_overloaded_storage_detection:
            summary.append('overloadedStorageDetection:   ' + str(overloaded_storage_detection) + ' (vs. default of ' + str(default_overloaded_storage_detection) + ')')
        if undersized_storage_detection != default_undersized_storage_detection:
            summary.append('undersizedStorageDetection:   ' + str(undersized_storage_detection) + ' (vs. default of ' + str(default_undersized_storage_detection) + ')')
        if slow_physical_storage_detection != default_slow_physical_storage_detection:
            summary.append('slowPhysicalStorageDetection: ' + str(slow_physical_storage_detection) + ' (vs. default of ' + str(default_slow_physical_storage_detection) + ')')
        if dropped_packets_detection != default_dropped_packets_detection:
            summary.append('droppedPacketsDetection:      ' + str(dropped_packets_detection) + ' (vs. default of ' + str(default_dropped_packets_detection) + ')')
        if low_datastore_space_detection != default_low_datastore_space_detection:
            summary.append('lowDatastoreSpaceDetection:   ' + str(low_datastore_space_detection) + ' (vs. default of ' + str(default_low_datastore_space_detection) + ')')

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
