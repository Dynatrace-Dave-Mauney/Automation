# Report manual tags on a specified monitored entity

import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []
    endpoint = '/api/v2/tags'
    # entity_name = 'SYNTHETIC_TEST-64750847343FE4CD'
    entity_name = 'HTTP_CHECK-8059BA7612A7C3F7'
    raw_params = f'entitySelector=entityId({entity_name})'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    manual_tags_json_list = dynatrace_api.get(env, token, endpoint, params)

    for manual_tags_json in manual_tags_json_list:
        inner_manual_tags_json_list = manual_tags_json.get('tags')
        for inner_manual_tags_json in inner_manual_tags_json_list:
            key = inner_manual_tags_json.get('key', '')
            value = inner_manual_tags_json.get('value', '')
            string_representation = inner_manual_tags_json.get('stringRepresentation', '')
            rows.append([key, value, string_representation, entity_name])

    rows = sorted(rows)
    report_name = 'Manual Tags'
    report_writer.initialize_text_file(None)
    report_headers = ('Key', 'Value', 'String Representation', 'Entity ID Tagged')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


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

    process(env, token)


if __name__ == '__main__':
    main()
