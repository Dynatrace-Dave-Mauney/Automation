from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    count_total = 0

    endpoint = '/api/config/v1/managementZones'
    params = ''
    management_zones_json_list = dynatrace_api.get(env, token, endpoint, params)

    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        for _ in inner_management_zones_json_list:
            count_total += 1

    return count_total


def main():
    rows = []
    grand_total = 0

    env_name, env, token = environment.get_environment('Prod')
    total = process(env, token)
    rows.append([env_name, total])
    grand_total += total

    env_name, env, token = environment.get_environment('NonProd')
    total = process(env, token)
    rows.append([env_name, total])
    grand_total += total

    rows.append(['Total', grand_total])

    report_name = 'Management Zone Counts'
    report_writer.initialize_text_file(None)
    report_headers = ('Environment', 'Management Zones')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    write_strings(['Grand Total: ' + str(grand_total)])
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


if __name__ == '__main__':
    main()
