from Reuse import dynatrace_api
from Reuse import environment

friendly_type_name = {'detectionRules/FULL_WEB_REQUEST': 'detectionRules (FULL_WEB_REQUEST)', 'detectionRules/FULL_WEB_SERVICE': 'detectionRules (FULL_WEB_SERVICE)', 'detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST': 'detectionRules (OPAQUE_AND_EXTERNAL_WEB_REQUEST)', 'detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE': 'detectionRules (OPAQUE_AND_EXTERNAL_WEB_SERVICE)', 'failureDetection/parameterSelection/parameterSets': 'failure detection parameter sets', 'failureDetection/parameterSelection/rules': 'failure detection parameter selection', 'ibmMQTracing/imsEntryQueue': 'ibm mq tracing ims entry queue', 'requestAttributes': 'request attributes', 'requestNaming': 'request naming'}


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    if print_mode:
        print('id' + '|' + 'name')

    # Custom Services by endpoint and language
    summary.append(process_custom_service_language(env, token, print_mode, 'java')[0])
    summary.append(process_custom_service_language(env, token, print_mode, 'dotNet')[0])
    summary.append(process_custom_service_language(env, token, print_mode, 'go')[0])
    summary.append(process_custom_service_language(env, token, print_mode, 'php')[0])
    # All others by "type" only
    summary.append(process_type(env, token, print_mode, 'detectionRules/FULL_WEB_REQUEST')[0])
    summary.append(process_type(env, token, print_mode, 'detectionRules/FULL_WEB_SERVICE')[0])
    summary.append(process_type(env, token, print_mode, 'detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST')[0])
    summary.append(process_type(env, token, print_mode, 'detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE')[0])
    summary.append(process_type(env, token, print_mode, 'failureDetection/parameterSelection/parameterSets')[0])
    summary.append(process_type(env, token, print_mode, 'failureDetection/parameterSelection/rules')[0])
    # reports a 410 - Gone now...
    # summary.append(process_type(env, token, print_mode, 'ibmMQTracing/imsEntryQueue')[0])
    summary.append(process_type(env, token, print_mode, 'requestAttributes')[0])

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def process_type(env, token, print_mode, entity_type):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/service/' + entity_type
    params = ''
    service_settings_json_list = dynatrace_api.get(env, token, endpoint, params)

    for service_settings_json in service_settings_json_list:
        inner_service_settings_json_list = service_settings_json.get('values')
        for inner_service_settings_json in inner_service_settings_json_list:
            entity_id = inner_service_settings_json.get('id')
            name = inner_service_settings_json.get('name')

            if print_mode:
                print(entity_id + '|' + name)

            count_total += 1

    if print_mode:
        print('Total Service - ' + friendly_type_name[entity_type] + ' settings: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' service - ' + friendly_type_name[entity_type] + ' settings currently defined.')

    return summary


def process_custom_service_language(env, token, print_mode, language):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/service/customServices/' + language
    params = ''
    custom_services_json_list = dynatrace_api.get(env, token, endpoint, params)

    for custom_services_json in custom_services_json_list:
        inner_custom_services_json_list = custom_services_json.get('values')
        for inner_custom_services_json in inner_custom_services_json_list:
            entity_id = inner_custom_services_json.get('id')
            name = inner_custom_services_json.get('name')

            # for later if details of rules, etc. are needed from each custom_service...
            # endpoint = '/api/config/v1/custom_services/' + entity_id
            # params = ''
            # custom_service = dynatrace_api.get(env, token, endpoint, params)[0]

            if print_mode:
                print(entity_id + '|' + name)

            count_total += 1

    if print_mode:
        print('Total Service - custom service -' + language + ': ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' ' + language + ' custom services currently defined.')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)
        

def main():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
