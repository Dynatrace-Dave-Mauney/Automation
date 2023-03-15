import requests
import urllib.parse
import xlsxwriter

from inspect import currentframe

from Reuse import dynatrace_api
from Reuse import environment

xlsx_file_name =  '../../$Output/Reporting/Dashboards/DashboardViews.xlsx'
html_file_name = '../../$Output/Reporting/Dashboards/DashboardViews.html'

# env_name, env, token = environment.get_environment('Prod')
# env_name, env, token = environment.get_environment('Prep')
# env_name, env, token = environment.get_environment('Dev')
env_name, env, token = environment.get_environment('Personal')
# env_name, env, token = environment.get_environment('FreeTrial1')


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def process():
    print(f'XSLX File: {xlsx_file_name}')
    print(f'HTML File: {html_file_name}')
    lines = []

    dashboard_details = load_dashboard_details()

    # For testing double-check of get_dashboard
    # dashboard_details = {}

    endpoint = '/api/v2/metrics/query'
    metric_schema_id = 'builtin:dashboards.viewCount'
    metric_query_options = ':splitBy("id"):avg:auto:sort(value(avg,descending)):fold:limit(100)'
    from_time = 'now-1M'
    params = 'metricSelector=' + urllib.parse.quote(metric_schema_id) + metric_query_options + '&from=' + from_time
    metrics_json_list = dynatrace_api.get(env, token, endpoint, params)
    for metrics_json in metrics_json_list:
        result_list = metrics_json.get('result')
        for result in result_list:
            data = result.get('data')
            for datapoint in data:
                values = datapoint.get('values')[0]
                dashboard_id = datapoint.get('dimensionMap').get('id').strip()
                dashboard_detail = dashboard_details.get(dashboard_id)
                if dashboard_detail:
                    dashboard_name = dashboard_detail.get('name', '')
                    dashboard_owner = dashboard_detail.get('owner', '')
                else:
                    # If user is not in "dynatrace.com", then they will get this for all "dynatrace.com" owners.
                    # So, we will double-check any missing ID by attempting to get it directly from the API
                    dashboard = get_dashboard(dashboard_id)
                    if dashboard:
                        dashboard_name = dashboard.get('dashboardMetadata').get('name', '')
                        dashboard_owner = dashboard.get('dashboardMetadata').get('owner', '')
                    else:
                        dashboard_name = '*** DELETED ***'
                        dashboard_owner = ''

                lines.append(f'{dashboard_name}|{dashboard_id}|{dashboard_owner}|{str(values)}')

    for line in lines:
        print(line)

    write_xlsx(lines)
    write_html(lines)


def load_dashboard_details():
    dashboard_details = {}

    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboards_json_list = dynatrace_api.get(env, token, endpoint, params)

    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')
            name = inner_dashboards_json.get('name')
            owner = inner_dashboards_json.get('owner')
            dashboard_details[entity_id] = {'name': name, 'owner': owner}

    return dashboard_details

def get_dashboard(dashboard_id):
    endpoint = f'/api/config/v1/dashboards/{dashboard_id}'
    params = ''
    dashboard_json_list = dynatrace_api.get(env, token, endpoint, params)
    if dashboard_json_list:
        dashboard = dashboard_json_list[0]
        if dashboard.get('dashboardMetadata'):
            return dashboard

    # Dashboard was not successfully retrieved
    return None


def write_xlsx(lines):
    workbook = xlsxwriter.Workbook(xlsx_file_name)
    header_format = workbook.add_format({'bold': True, 'bg_color': '#B7C9E2'})
    number_format = workbook.add_format({'num_format': '0'})

    worksheet = workbook.add_worksheet('Dashboard Views')

    row_index = 0
    # column_index = 0

    headers = ['Dashboard Name', 'Dashboard ID', 'Owner', 'Views']
    worksheet.write(row_index, 0, headers[0], header_format)
    worksheet.write(row_index, 1, headers[1], header_format)
    worksheet.write(row_index, 2, headers[2], header_format)
    worksheet.write(row_index, 3, headers[3], header_format)
    row_index += 1


    for line in lines:
        columns = line.split('|')
        worksheet.write(row_index, 0, columns[0])
        worksheet.write(row_index, 1, columns[1])
        worksheet.write(row_index, 2, columns[2])
        worksheet.write(row_index, 3, int(columns[3]), number_format)
        row_index += 1

    worksheet.autofilter(0, 2, row_index, 2) # add filter to only the third column (owner)
    worksheet.autofit()
    workbook.close()


def write_html(lines):
    html_top = '''<html>
      <body>
        <head>
          <style>
            table, th, td {
              border: 1px solid black;
              border-collapse: collapse;
            }
            th, td {
              padding: 5px;
            }
            th {
              text-align: left;
            }
          </style>
        </head>'''

    table_header = '''    <table>
          <tr>
            <th>Dashboard Name</th>
            <th>Dashboard ID</th>
            <th>Owner</th>
            <th>Views</th>
          </tr>'''

    html_bottom = '''    </table>
      </body>
    </html>'''

    row_start = '<tr>'
    row_end = '</tr>'
    col_start = '<td>'
    col_end = '</td>'

    with open(html_file_name, 'w', encoding='utf8') as file:
        # Begin HTML formatting
        write_line(file, html_top)

        # Write the tag summary header
        write_h1_heading(file, f'Dashboard Views')

        # Write Table Header
        write_line(file, table_header)

        # Write Table Rows
        for line in lines:
            columns = line.split('|')
            write_line(file, f'{row_start}{col_start}{columns[0]}{col_end}{col_start}{columns[1]}{col_end}{col_start}{columns[2]}{col_end}{col_start}{columns[3]}{col_end}{row_end}')

        # Finish the HTML formatting
        write_line(file, html_bottom)


def write_h1_heading(outfile, heading):
    outfile.write('    <h1>' + heading + '</h1>')
    outfile.write('\n')


def write_line(outfile, content):
    outfile.write(content)
    outfile.write('\n')


if __name__ == '__main__':
    process()
