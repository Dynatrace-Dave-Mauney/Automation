from Reuse import dynatrace_api
from Reuse import environment


friendly_type_name = {'allowedBeaconOriginsForCors': 'allowed beacon origins for CORS', 'applicationDetectionRules': 'application detection rules', 'applicationDetectionRules/hostDetection': 'host detection rules', 'contentResources': 'content resources', 'geographicRegions/ipDetectionHeaders': 'IP detection headers', 'geographicRegions/ipAddressMappings': 'IP address mappings', 'applications/mobile': 'mobile applications', 'applications/web': 'web applications'}
string_list_key = {'allowedBeaconOriginsForCors': 'allowedBeaconOrigins', 'applicationDetectionRules/hostDetection': 'hostDetectionHeaders', 'contentResources': 'resourceProviders', 'geographicRegions/ipDetectionHeaders': 'ipDetectionHeaders', 'geographicRegions/ipAddressMappings': 'ipAddressMappingRules'}


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    """ Process a mix of lists of values and more custom lists of strings with custom keys. """
    summary = []

    summary.extend(process_string_list(env, token, summary_mode, 'allowedBeaconOriginsForCors'))
    summary.extend(process_type(env, token, summary_mode, 'applicationDetectionRules'))
    summary.extend(process_string_list(env, token, summary_mode, 'applicationDetectionRules/hostDetection'))
    summary.extend(process_string_list(env, token, summary_mode, 'contentResources'))
    summary.extend(process_string_list(env, token, summary_mode, 'geographicRegions/ipDetectionHeaders'))
    summary.extend(process_string_list(env, token, summary_mode, 'geographicRegions/ipAddressMappings'))
    summary.extend(process_type(env, token, summary_mode, 'applications/mobile'))
    summary.extend(process_type(env, token, summary_mode, 'applications/web'))

    if not summary_mode:
        print_list(summary)

    return summary


def process_type(env, token, summary_mode, entity_type):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/' + entity_type
    rum_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    if not summary_mode:
        if entity_type == 'applications/web':
            print('id' + '|' + 'name' + '|' + 'realUserMonitoringEnabled' + '|' + 'sessionReplayConfig.enabled')
        else:
            print('id' + '|' + 'name')

    for rum_json in rum_json_list:
        inner_rum_json_list = rum_json.get('values')
        for inner_rum_json in inner_rum_json_list:
            entity_id = inner_rum_json.get('id')
            name = inner_rum_json.get('name')

            if not summary_mode:
                print(entity_id + '|' + name)

            count_total += 1

    if not summary_mode:
        print('Total RUM Rules - ' + friendly_type_name[entity_type] + ': ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' RUM rules for ' + friendly_type_name[entity_type] + ' currently defined.')

    return summary


def process_string_list(env, token, summary_mode, entity_type):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/' + entity_type
    rum_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    if not summary_mode:
        print(string_list_key[entity_type])

    for rum_json in rum_json_list:
        inner_rum_json_list = rum_json.get(string_list_key[entity_type])
        for inner_rum_string in inner_rum_json_list:

            if not summary_mode:
                print(inner_rum_string)

            count_total += 1

    if not summary_mode:
        print('Total RUM Rules - ' + friendly_type_name[entity_type] + ': ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' RUM rules for ' + friendly_type_name[entity_type] + ' currently defined.')

    return summary


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
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
