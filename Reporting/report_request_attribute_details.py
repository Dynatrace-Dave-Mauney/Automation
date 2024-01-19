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

    endpoint = '/api/config/v1/service/requestAttributes'
    request_attributes_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for request_attributes_json in request_attributes_json_list:
        inner_request_attributes_json_list = request_attributes_json.get('values')
        for inner_request_attributes_json in inner_request_attributes_json_list:
            entity_id = inner_request_attributes_json.get('id')
            name = inner_request_attributes_json.get('name')

            # If more details are ever needed
            # endpoint = '/api/config/v1/service/requestAttributes/' + entity_id
            # r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
            # request_attribute = r.json()

            if not summary_mode:
                rows.append((name, entity_id))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' request attributes currently defined.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Request Attributes'
        report_writer.initialize_text_file(None)
        report_headers = ('name', 'id')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total request_attributes: ' + str(count_total)])
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
