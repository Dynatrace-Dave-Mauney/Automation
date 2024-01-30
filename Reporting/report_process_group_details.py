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
    counts_primary_icon_type = {}

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(PROCESS_GROUP)&fields=+properties,+icon&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            properties = inner_entities_json.get('properties')
            detected_name = properties.get('detectedName', '')
            metadata = str(properties.get('metadata', ''))
            metadata = metadata.replace("{", "")
            metadata = metadata.replace("}", "")
            metadata = metadata.replace("[", "")
            metadata = metadata.replace("]", "")
            metadata = metadata.replace(" 'value':", ":")
            metadata = metadata.replace("'key':", "")
            metadata = metadata.replace(" '", "")
            metadata = metadata.replace("',", "")
            metadata = metadata.replace("'", "")
            listen_ports = str(properties.get('listenPorts', ''))
            listen_ports = listen_ports.replace('[', '')
            listen_ports = listen_ports.replace(']', '')

            icon = inner_entities_json.get('icon')
            if icon:
                primary_icon_type = icon.get('primaryIconType')
            else:
                primary_icon_type = 'NONE'

            if not summary_mode:
                rows.append((display_name, detected_name, entity_id, metadata, listen_ports, primary_icon_type))

            count_total += 1
            counts_primary_icon_type[primary_icon_type] = counts_primary_icon_type.get(primary_icon_type, 0) + 1

    counts_primary_icon_type_str = str(sorted(counts_primary_icon_type.items()))
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace('[', '')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace(']', '')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace('), (', '~COMMA~')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace('(', '')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace(')', '')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace(',', ':')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace('~COMMA~', ', ')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace("'", "")

    summary.append('There are ' + str(count_total) + ' process groups being monitored.  ')
    if count_total > 0:
        summary.append('The primary technology breakdown is ' + counts_primary_icon_type_str + '.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Process Groups'
        report_writer.initialize_text_file(None)
        report_headers = ('displayName', 'detectedName', 'entityId', 'metadata', 'listenPorts', 'primaryIconType')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Process Groups: ' + str(count_total)])
        write_strings(['Primary Icon Type Counts: ' + counts_primary_icon_type_str])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


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
