import dynatrace_rest_api_helper
import os


friendly_type_name = {'allowedBeaconOriginsForCors': 'allowed beacon origins for CORS', 'applicationDetectionRules': 'application detection rules', 'applicationDetectionRules/hostDetection': 'host detection rules', 'contentResources': 'content resources', 'geographicRegions/ipDetectionHeaders': 'IP detection headers', 'geographicRegions/ipAddressMappings': 'IP address mappings', 'applications/mobile': 'mobile applications', 'applications/web': 'web applications'}
string_list_key = {'allowedBeaconOriginsForCors': 'allowedBeaconOrigins', 'applicationDetectionRules/hostDetection': 'hostDetectionHeaders', 'contentResources': 'resourceProviders', 'geographicRegions/ipDetectionHeaders': 'ipDetectionHeaders', 'geographicRegions/ipAddressMappings': 'ipAddressMappingRules'}


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    """ Process a mix of lists of values and more custom lists of strings with custom keys. """
    summary = []

    summary.extend(process_string_list(env, token, print_mode, 'allowedBeaconOriginsForCors'))
    summary.extend(process_type(env, token, print_mode, 'applicationDetectionRules'))
    summary.extend(process_string_list(env, token, print_mode, 'applicationDetectionRules/hostDetection'))
    summary.extend(process_string_list(env, token, print_mode, 'contentResources'))
    summary.extend(process_string_list(env, token, print_mode, 'geographicRegions/ipDetectionHeaders'))
    summary.extend(process_string_list(env, token, print_mode, 'geographicRegions/ipAddressMappings'))
    summary.extend(process_type(env, token, print_mode, 'applications/mobile'))
    summary.extend(process_type(env, token, print_mode, 'applications/web'))

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def process_type(env, token, print_mode, entity_type):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/' + entity_type
    params = ''
    rum_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)

    if print_mode:
        if entity_type == 'applications/web':
            print('id' + '|' + 'name' + '|' + 'realUserMonitoringEnabled' + '|' + 'sessionReplayConfig.enabled')
        else:
            print('id' + '|' + 'name')

    for rum_json in rum_json_list:
        inner_rum_json_list = rum_json.get('values')
        for inner_rum_json in inner_rum_json_list:
            entity_id = inner_rum_json.get('id')
            name = inner_rum_json.get('name')

            if print_mode:
                print(entity_id + '|' + name)

            count_total += 1

    if print_mode:
        print('Total RUM Rules - ' + friendly_type_name[entity_type] + ': ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' RUM rules for ' + friendly_type_name[entity_type] + ' currently defined.')

    return summary


def process_string_list(env, token, print_mode, entity_type):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/' + entity_type
    params = ''
    rum_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)

    if print_mode:
        print(string_list_key[entity_type])

    for rum_json in rum_json_list:
        inner_rum_json_list = rum_json.get(string_list_key[entity_type])
        for inner_rum_string in inner_rum_json_list:

            if print_mode:
                print(inner_rum_string)

            count_total += 1

    if print_mode:
        print('Total RUM Rules - ' + friendly_type_name[entity_type] + ': ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' RUM rules for ' + friendly_type_name[entity_type] + ' currently defined.')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


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
