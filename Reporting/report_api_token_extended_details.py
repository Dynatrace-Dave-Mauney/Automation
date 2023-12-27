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
    count_dynatrace_owner = 0
    count_last_used_date_none = 0
    count_too_many_scopes = 0

    too_many_scopes_threshold = 10

    endpoint = '/api/v2/apiTokens'
    api_tokens_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for api_tokens_json in api_tokens_json_list:
        inner_api_tokens_json_list = api_tokens_json.get('apiTokens')
        for inner_api_tokens_json in inner_api_tokens_json_list:
            entity_id = inner_api_tokens_json.get('id')
            name = inner_api_tokens_json.get('name')
            enabled = inner_api_tokens_json.get('enabled')
            owner = inner_api_tokens_json.get('owner')
            creation_date = inner_api_tokens_json.get('creationDate')

            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            api_token = r.json()

            last_used_date = api_token.get('lastUsedDate')
            scopes = api_token.get('scopes')

            if not summary_mode:
                rows.append((name, entity_id, str(enabled), owner, creation_date, last_used_date, report_writer.stringify_list(scopes)))

            count_total += 1

            if owner.lower().endswith('dynatrace.com'):
                count_dynatrace_owner += 1

            if not last_used_date:
                count_last_used_date_none += 1

            if len(scopes) > too_many_scopes_threshold:
                count_too_many_scopes += 1

    summary.append(f'There are {count_total} API tokens currently available.')
    summary.append(f'There are {count_last_used_date_none} API Tokens with no Last Used Date.')
    summary.append(f'There are {count_too_many_scopes} API Tokens with more than {too_many_scopes_threshold} scopes.')
    summary.append(f'There are {count_dynatrace_owner} API Tokens owned by a Dynatrace employee.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = ''
        report_writer.initialize_text_file(None)
        report_headers = ('Name', 'ID', 'Enabled', 'Owner', 'Creation Date', 'Last Used Date', 'Scopes')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings([f'Total API Tokens: {count_total}'])
        write_strings([f'API Tokens with no Last Used Date: {count_last_used_date_none}'])
        write_strings([f'API Tokens with more than {too_many_scopes_threshold} scopes: {count_too_many_scopes}'])
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
