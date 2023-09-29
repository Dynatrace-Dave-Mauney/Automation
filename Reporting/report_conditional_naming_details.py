from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


friendly_type_name = {'processGroup': 'Process Groups', 'host': 'Hosts', 'service': 'Services'}


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []
    count_total = 0 

    type_rows, type_summary, type_count = process_type(env, token, summary_mode, 'processGroup')
    rows.extend(type_rows)
    summary.extend(type_summary)
    count_total += type_count
    type_rows, type_summary, type_count = process_type(env, token, summary_mode, 'host')
    rows.extend(type_rows)
    summary.extend(type_summary)
    count_total += type_count
    type_rows, type_summary, type_count = process_type(env, token, summary_mode, 'service')
    rows.extend(type_rows)
    summary.extend(type_summary)
    count_total += type_count

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Conditional Naming Rules'
        report_writer.initialize_text_file(None)
        report_headers = ('name', 'id', 'type')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Conditional Naming Rules: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def process_type(env, token, summary_mode, entity_type):
    summary = []
    rows = []
    count_total = 0

    endpoint = '/api/config/v1/conditionalNaming/' + entity_type
    params = ''
    conditional_naming_json_list = dynatrace_api.get(env, token, endpoint, params)

    for conditional_naming_json in conditional_naming_json_list:
        inner_conditional_naming_json_list = conditional_naming_json.get('values')
        for inner_conditional_naming_json in inner_conditional_naming_json_list:
            entity_id = inner_conditional_naming_json.get('id')
            name = inner_conditional_naming_json.get('name')

            if not summary_mode:
                rows.append((name, entity_id, friendly_type_name[entity_type]))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' conditional naming rules for ' + friendly_type_name[entity_type] + ' currently defined.')

    return rows, summary, count_total


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
