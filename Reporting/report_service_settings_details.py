from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

friendly_type_name = {'detectionRules/FULL_WEB_REQUEST': 'detectionRules (FULL_WEB_REQUEST)', 'detectionRules/FULL_WEB_SERVICE': 'detectionRules (FULL_WEB_SERVICE)', 'detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST': 'detectionRules (OPAQUE_AND_EXTERNAL_WEB_REQUEST)', 'detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE': 'detectionRules (OPAQUE_AND_EXTERNAL_WEB_SERVICE)', 'failureDetection/parameterSelection/parameterSets': 'failure detection parameter sets', 'failureDetection/parameterSelection/rules': 'failure detection parameter selection', 'ibmMQTracing/imsEntryQueue': 'ibm mq tracing ims entry queue', 'requestAttributes': 'request attributes', 'requestNaming': 'request naming'}


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []

    # Custom Services by endpoint and language
    summary.append(process_custom_service_language(env, token, summary_mode, 'java', rows)[0])
    summary.append(process_custom_service_language(env, token, summary_mode, 'dotNet', rows)[0])
    summary.append(process_custom_service_language(env, token, summary_mode, 'go', rows)[0])
    summary.append(process_custom_service_language(env, token, summary_mode, 'php', rows)[0])
    # All others by "type" only
    summary.append(process_type(env, token, summary_mode, 'detectionRules/FULL_WEB_REQUEST', rows)[0])
    summary.append(process_type(env, token, summary_mode, 'detectionRules/FULL_WEB_SERVICE', rows)[0])
    summary.append(process_type(env, token, summary_mode, 'detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST', rows)[0])
    summary.append(process_type(env, token, summary_mode, 'detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE', rows)[0])
    summary.append(process_type(env, token, summary_mode, 'failureDetection/parameterSelection/parameterSets', rows)[0])
    summary.append(process_type(env, token, summary_mode, 'failureDetection/parameterSelection/rules', rows)[0])
    # reports a 410 - Gone now...
    # summary.append(process_type(env, token, summary_mode, 'ibmMQTracing/imsEntryQueue', rows)[0])
    summary.append(process_type(env, token, summary_mode, 'requestAttributes', rows)[0])

    if not summary_mode:
        report_name = 'Service Settings'
        report_writer.initialize_text_file(None)
        report_headers = ('Language/Entity Type', 'Name', 'Entity ID')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        # write_strings(['Total Service Settings: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def process_type(env, token, summary_mode, entity_type, rows):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/service'
    service_settings_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}/{entity_type}', token)

    for service_settings_json in service_settings_json_list:
        inner_service_settings_json_list = service_settings_json.get('values')
        for inner_service_settings_json in inner_service_settings_json_list:
            entity_id = inner_service_settings_json.get('id')
            name = inner_service_settings_json.get('name')

            if not summary_mode:
                rows.append((entity_type, name, entity_id))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' service - ' + friendly_type_name[entity_type] + ' settings currently defined.')

    return summary


def process_custom_service_language(env, token, summary_mode, language, rows):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/service/customServices'
    custom_services_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}/{language}', token)

    for custom_services_json in custom_services_json_list:
        inner_custom_services_json_list = custom_services_json.get('values')
        for inner_custom_services_json in inner_custom_services_json_list:
            entity_id = inner_custom_services_json.get('id')
            name = inner_custom_services_json.get('name')

            # for later if details of rules, etc. are needed from each custom_service...
            # endpoint = '/api/config/v1/custom_services'
            # r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            # custom_service = r.json()

            if not summary_mode:
                rows.append((f'Custom Service: {language}', name, entity_id))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' ' + language + ' custom services currently defined.')

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


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
