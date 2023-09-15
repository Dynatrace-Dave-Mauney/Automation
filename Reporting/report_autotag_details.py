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

    endpoint = '/api/config/v1/autoTags'
    params = ''
    autotags_json_list = dynatrace_api.get(env, token, endpoint, params)

    for autotags_json in autotags_json_list:
        inner_autotags_json_list = autotags_json.get('values')
        for inner_autotags_json in inner_autotags_json_list:
            entity_id = inner_autotags_json.get('id')
            name = inner_autotags_json.get('name')

            # for later if details of rules, etc. are needed from each autotag...
            endpoint = '/api/config/v1/autoTags/' + entity_id
            params = ''
            autotag = dynatrace_api.get(env, token, endpoint, params)[0]

            rules = autotag.get('rules')

            if not summary_mode:
                rows.append((name, entity_id, str(rules)))

            count_total += 1

    rows = sorted(rows)

    summary.append('There are ' + str(count_total) + ' automatically applied tags currently defined.')

    if not summary_mode:
        report_name = 'Automatic Tags'
        report_writer.initialize_text_file(None)
        report_headers = ('name', 'id', 'rules')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Automatically Applied Tags: ' + str(count_total)])
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
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
