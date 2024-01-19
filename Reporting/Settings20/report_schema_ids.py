from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []
    endpoint = '/api/v2/settings/schemas'
    settings_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    # schema_ids = []
    # schema_dict = {}

    for settings_json in settings_json_list:
        inner_settings_json_list = settings_json.get('items')
        for inner_settings_json in inner_settings_json_list:
            schema_id = inner_settings_json.get('schemaId')
            # schema_ids.append(schema_id)
            rows.append([schema_id])
            # latest_schema_version = inner_settings_json.get('latestSchemaVersion')
            # schema_dict[schema_id] = latest_schema_version

    rows = sorted(rows)
    report_name = 'Settings 2.0 Schemas'
    report_writer.initialize_text_file(None)
    report_headers = (['schemaId'])
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
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)


if __name__ == '__main__':
    main()
