import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    endpoint = '/api/config/v1/autoTags'
    raw_params = 'fields=+description'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    auto_tags_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    rows = []

    for auto_tags_json in auto_tags_json_list:
        inner_auto_tags_json_list = auto_tags_json.get('values')
        for inner_auto_tags_json in inner_auto_tags_json_list:
            name = inner_auto_tags_json.get('name')
            description = inner_auto_tags_json.get('description', '')
            rows.append((name, description))

    report_name = 'Automatic Tags'
    report_writer.initialize_text_file(None)
    report_headers = ('name', 'description')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


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
