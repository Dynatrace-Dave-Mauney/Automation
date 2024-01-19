import urllib.parse

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

    count_total = 0
    counts_service_type = {}
    counts_service_technology_types = {}

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(SERVICE)&fields=+properties,+fromRelationships&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            display_name = inner_entities_json.get('displayName')
            properties = inner_entities_json.get('properties')
            service_type = properties.get('serviceType', 'NONE')

            if service_type != 'BACKGROUND_ACTIVITY':
                continue

            entity_id = inner_entities_json.get('entityId')
            detected_name = properties.get('detectedName', '')
            counts_service_type[service_type] = counts_service_type.get(service_type, 0) + 1
            service_technology_types = str(properties.get('serviceTechnologyTypes', 'NONE'))
            service_technology_types = service_technology_types.replace('[', '')
            service_technology_types = service_technology_types.replace(']', '')
            service_technology_types = service_technology_types.replace("'", "")
            counts_service_technology_types[service_technology_types] = counts_service_technology_types.get(
                service_technology_types, 0) + 1

            if not summary_mode:
                rows.append(
                    (display_name, entity_id, detected_name, service_type, service_technology_types))

            count_total += 1

    counts_service_type_str = sort_and_stringify_dictionary_items(counts_service_type)
    counts_service_technology_types_str = sort_and_stringify_dictionary_items(counts_service_technology_types)

    summary.append('There are ' + str(count_total) + ' external services currently being monitored.  ')
    if count_total > 0 and counts_service_type:
        summary.append('The Service Type breakdown is ' + counts_service_type_str + '.  ')
    if count_total > 0 and counts_service_technology_types:
        summary.append('The External Service Technology Type breakdown is ' + counts_service_technology_types_str + '.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Services'
        report_writer.initialize_text_file(None)
        report_headers = ('Display Name', 'Entity ID', 'Detected Name', 'Service Type', 'Service Technology Types')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings([f'Total External Services: {count_total}'])
        # write_strings([f'External Service Type Counts: {counts_service_type_str}'])
        write_strings([f'External Service Technology Types Counts: {counts_service_technology_types_str}'])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def sort_and_stringify_dictionary_items(any_dict):
    dict_str = str(sorted(any_dict.items()))
    dict_str = dict_str.replace('[', '')
    dict_str = dict_str.replace(']', '')
    dict_str = dict_str.replace('), (', '~COMMA~')
    dict_str = dict_str.replace('(', '')
    dict_str = dict_str.replace(')', '')
    dict_str = dict_str.replace(',', ':')
    dict_str = dict_str.replace('~COMMA~', ', ')
    dict_str = dict_str.replace("'", "")
    return dict_str


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
