import copy

from Reuse import environment
from Reuse import report_writer

"""
Read the previously generated "report_management_zone_slo_coverage.txt" file and the
"report_management_zone_coverage.txt" file and determine which SLO types are not covered
that should be.

If a management zone "contains" one of the entities that "require" SLOs, but has not SLO yet
defined, it will be "called out" as lacking coverage for that entity type.

"""


def process():
    """
    Input file names:
    report_management_zone_slo_coverage.txt
    report_management_zone_coverage.txt
    """
    management_zone_slo_coverage_file_name = environment.get_configuration('report_management_zone_slo_coverage_details.slo_coverage_file_name')
    management_zone_coverage_file_name = environment.get_configuration('report_management_zone_slo_coverage_details.coverage_file_name')

    print(management_zone_slo_coverage_file_name)
    print(management_zone_coverage_file_name)

    with open(management_zone_slo_coverage_file_name, 'r', encoding='utf-8') as management_zone_slo_coverage_file:
        management_zone_slo_coverage_content = management_zone_slo_coverage_file.readlines()
        # print(management_zone_slo_coverage_content)

    management_zone_slo_coverage_dict = {}

    line_number = 1
    headers = ''
    for line in management_zone_slo_coverage_content:
        columns = line.strip().split('|')
        if line_number == 2:
            headers = copy.deepcopy(columns)
        if line_number > 2:
            # print(f'{line_number}: {line}')
            # print(headers)
            # print(columns)
            management_zone_slo_coverage_dict[columns[0]] = {
                headers[1]: int(columns[1]),
                headers[2]: int(columns[2]),
                headers[3]: int(columns[3]),
                headers[4]: int(columns[4]),
                headers[5]: int(columns[5]),
                headers[6]: int(columns[6]),
                headers[7]: int(columns[7])
            }
        line_number += 1

    # print(management_zone_slo_coverage_dict)

    with open(management_zone_coverage_file_name, 'r', encoding='utf-8') as management_zone_coverage_file:
        management_zone_coverage_content = management_zone_coverage_file.readlines()
        # print(management_zone_coverage_content)

    management_zone_coverage_dict = {}

    line_number = 1
    headers = ''
    for line in management_zone_coverage_content:
        columns = line.strip().split('|')
        if line_number == 2:
            headers = copy.deepcopy(columns)
        if line_number > 2:
            # print(f'{line_number}: {line}')
            # print(headers)
            # print(columns)
            management_zone_coverage_dict[columns[0]] = {
                headers[1]: int(columns[1]),    # APPLICATION
                headers[20]: int(columns[20]),  # HOST
                headers[21]: int(columns[21]),  # HTTP_CHECK
                headers[25]: int(columns[25]),  # MOBILE_APPLICATION
                headers[27]: int(columns[27]),  # SERVICE
                headers[28]: int(columns[28])   # SYNTHETIC_TEST
            }
        line_number += 1

    # print(management_zone_coverage_dict)

    # management_zone_slo_coverage_details_dict = generate_management_zone_slo_coverage_details_dict(management_zone_slo_coverage_dict, management_zone_coverage_dict)

    # print(management_zone_slo_coverage_details_dict)

    rows = []
    for key in sorted(management_zone_slo_coverage_dict.keys()):
        http_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'HTTP', 'HTTP_CHECK')
        browser_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'Browser', 'SYNTHETIC_TEST')
        host_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'Host', 'HOST')
        service_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'Service', 'SERVICE')
        mobile_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'Mobile', 'MOBILE_APPLICATION')
        web_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'Web', 'APPLICATION')
        rows.append((key, browser_coverage_indicator, http_coverage_indicator, service_coverage_indicator, host_coverage_indicator, mobile_coverage_indicator, web_coverage_indicator))

    rows = sorted(rows)
    report_name = 'MZ-SLO Cross-Reference Gaps'
    report_writer.initialize_text_file(None)
    report_headers = ('Management Zone', 'Browser', 'HTTP', 'Service', 'Host', 'Mobile', 'Web')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)

    rows = minimize_rows(rows)
    report_name = 'MZ-SLO Cross-Reference Gaps'
    report_writer.initialize_text_file('report_management_zone_slo_coverage_gaps_minimized.txt')
    report_headers = ('Management Zone', 'Browser', 'HTTP', 'Service', 'Host', 'Mobile', 'Web')
    print('')
    print('Minimized Report:')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text('report_management_zone_slo_coverage_gaps_minimized.txt', report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx('report_management_zone_slo_coverage_gaps_minimized.xlsx', report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html('report_management_zone_slo_coverage_gaps_minimized.html', report_name, report_headers, rows)


def minimize_rows(rows):
    minimized_rows = []
    for row in rows:
        # if row[1] == 'N' or row[2] == 'N' or row[3] == 'N' or row[4] == 'N' or row[5] == 'N' or row[6] == 'N':
        if row[1] == 'N' or row[2] == 'N' or row[3] == 'N' or row[4] == 'N':
            minimized_rows.append(row)

    return minimized_rows


def generate_management_zone_slo_coverage_details_dict(management_zone_slo_coverage_dict, management_zone_coverage_dict):
    management_zone_slo_coverage_details_dict = {}

    keys = management_zone_slo_coverage_dict.keys()
    for key in sorted(keys):
        http_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'HTTP', 'HTTP_CHECK')
        browser_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'Browser', 'SYNTHETIC_TEST')
        host_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'Host', 'HOST')
        service_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'Service', 'SERVICE')
        mobile_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'Mobile', 'MOBILE_APPLICATION')
        web_coverage_indicator = get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, key, 'Web', 'APPLICATION')
        management_zone_slo_coverage_details_dict[key] = {'Browser': browser_coverage_indicator, 'HTTP': http_coverage_indicator, 'Service': service_coverage_indicator, 'Host': host_coverage_indicator, 'Mobile': mobile_coverage_indicator, 'Web': web_coverage_indicator}

    return management_zone_slo_coverage_details_dict


def get_coverage_indicator(management_zone_slo_coverage_dict, management_zone_coverage_dict, management_zone_name, key_slo_coverage, key_coverage):
    try:
        if management_zone_slo_coverage_dict[management_zone_name][key_slo_coverage] == 0 and \
                management_zone_coverage_dict[management_zone_name][key_coverage] > 0:
            return 'N'
        else:
            if management_zone_slo_coverage_dict[management_zone_name][key_slo_coverage] == 0 and \
                    management_zone_coverage_dict[management_zone_name][key_coverage] == 0:
                return '-'
            else:
                if management_zone_slo_coverage_dict[management_zone_name][key_slo_coverage] > 0:
                    return 'Y'
                else:
                    return 'Logic Error!'
    except KeyError:
        print(f'Management zone {management_zone_name} key error!')
        return 'Unknown Coverage'


def main():
    process()
    
    
if __name__ == '__main__':
    main()
