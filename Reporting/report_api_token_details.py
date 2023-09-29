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

    endpoint = '/api/v2/apiTokens'
    params = ''
    activegates_json_list = dynatrace_api.get(env, token, endpoint, params)

    for activegates_json in activegates_json_list:
        inner_activegates_json_list = activegates_json.get('apiTokens')
        for inner_activegates_json in inner_activegates_json_list:
            entity_id = inner_activegates_json.get('id')
            name = inner_activegates_json.get('name')
            enabled = inner_activegates_json.get('enabled')
            owner = inner_activegates_json.get('owner')
            creation_date = inner_activegates_json.get('creationDate')

            if not summary_mode:
                rows.append((name, entity_id, str(enabled), owner, creation_date))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' API tokens currently available.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = ''
        report_writer.initialize_text_file(None)
        report_headers = ('name', 'id', 'enabled', 'owner', 'creationDate')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total API Tokens: ' + str(count_total)])
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
