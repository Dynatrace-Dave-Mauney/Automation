# Report on various tagged entities with an emphasis on finding tags that are key-only rather than key/value pairs.

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
    count_key_only = 0
    count_key_value = 0

    counts_entity_type = {}
    counts_entity_type_key_only = {}
    counts_entity_type_key_value = {}

    endpoint = '/api/v2/tags'
    
    # Skipping for now: 'ESXi', 'AWS', 'Azure scale set', 'Custom device', 'Custom device group'
    taggable_entity_list = [('APPLICATION', 'Applications'), ('SYNTHETIC_TEST', 'Browser Monitors'), ('HTTP_CHECK', 'Http Monitors'), ('SERVICE', 'Services'), ('HOST', 'Hosts'), ('PROCESS_GROUP', 'Process groups'), ('PROCESS_GROUP_INSTANCE', 'Processes')]

    for taggable_entity in taggable_entity_list:
        entity_type = taggable_entity[0]
        entity_name = taggable_entity[1]

        raw_params = f'entitySelector=type({entity_type})'
        params = urllib.parse.quote(raw_params, safe='/,&=')
        manual_tags_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

        for manual_tags_json in manual_tags_json_list:
            inner_manual_tags_json_list = manual_tags_json.get('tags')
            for inner_manual_tags_json in inner_manual_tags_json_list:
                key = inner_manual_tags_json.get('key', '')
                value = inner_manual_tags_json.get('value', '')
                string_representation = inner_manual_tags_json.get('stringRepresentation', '')
    
                if not summary_mode:
                    rows.append((key, value, string_representation, entity_name, entity_type))

                count_total += 1
                counts_entity_type[entity_type] = counts_entity_type.get(entity_type, 0) + 1

                if value == '':
                    count_key_only += 1
                    counts_entity_type_key_only[entity_type] = counts_entity_type_key_only.get(entity_type, 0) + 1
                else:
                    count_key_value += 1
                    counts_entity_type_key_value[entity_type] = counts_entity_type_key_value.get(entity_type, 0) + 1

        count_entity_type = counts_entity_type.get(entity_type, 0)
        count_entity_type_key_only = counts_entity_type_key_only.get(entity_type, 0)
        count_entity_type_key_value = counts_entity_type_key_value.get(entity_type, 0)

        count_entity_type_message = f'There are {count_entity_type} manual tags currently defined for {entity_name}'
        if count_entity_type > 0:
            summary.append(f'{count_entity_type_message}.  {count_entity_type_key_only} are key only and {count_entity_type_key_value} are key/value pairs.')
        else:
            summary.append(f'{count_entity_type_message}.')

    if not summary_mode:
        report_name = 'Custom Tags'
        report_writer.initialize_text_file(None)
        report_headers = ('Key', 'Value', 'String Representation', 'Entity Tagged', 'Entity Type')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Manual Tags: ' + str(count_total)])
        write_strings(['Total Key Only Manual Tags: ' + str(count_key_only)])
        write_strings(['Total Key/Value Manual Tags: ' + str(count_key_value)])
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
    env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
