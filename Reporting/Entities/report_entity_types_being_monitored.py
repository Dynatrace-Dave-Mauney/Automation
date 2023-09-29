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
    count_monitored_entity_types_total = 0
    count_monitored_total = 0

    endpoint = '/api/v2/entityTypes'
    params = ''
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('types')
        for inner_entities_json in inner_entities_json_list:
            entity_type = inner_entities_json.get('type')
            display_name = inner_entities_json.get('displayName')
            # Use "True" for all entity types, or select the ones to be reported
            # if entity_type.startswith('cloud:aws'):
            if True:
                endpoint = '/api/v2/entities'
                entity_selector = 'type(' + entity_type + ')'
                params = '&entitySelector=' + urllib.parse.quote(entity_selector)
                entity_type_json_list = dynatrace_api.get(env, token, endpoint, params)
                total_count = entity_type_json_list[0].get('totalCount')
                if total_count > 0:
                    rows.append((entity_type, display_name, str(total_count)))
                    count_monitored_entity_types_total += 1
                    count_monitored_total += total_count

            count_total += 1

    summary.append('There are ' + str(count_total) + ' entity types currently defined, ' + str(count_monitored_entity_types_total) + ' entity types being monitored and a total of ' + str(count_monitored_total) + ' entities being monitored.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Entity Types Monitored'
        report_writer.initialize_text_file(None)
        report_headers = ('id', 'name', 'monitored entity count')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Entities Defined: ' + str(count_total)])
        write_strings(['Total Entity Types Monitored: ' + str(count_monitored_entity_types_total)])
        write_strings(['Total Entities Monitored: ' + str(count_monitored_total)])
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
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)


if __name__ == '__main__':
    main()
