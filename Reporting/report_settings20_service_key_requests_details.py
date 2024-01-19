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

    schema_id = 'builtin:settings.subscriptions.service'

    endpoint = '/api/v2/settings/objects'
    raw_params = f'schemaIds={schema_id}&fields=value,scope&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for settings_object in settings_object_list:
        # print(settings_object)
        items = settings_object.get('items')
        for item in items:
            # print(item)
            if not summary_mode:
                scope = item.get('scope')
                value = item.get('value')
                # print(value)
                key_request_list = value.get('keyRequestNames')
                for key_request in key_request_list:
                    rows.append([key_request, scope])

            count_total += 1

    summary.append(f'There are {count_total} service key requests currently defined.')

    summary = sorted(summary)

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Service Key Requests'
        report_writer.initialize_text_file(None)
        report_headers = ['Key Request', 'Scope']
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
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
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
