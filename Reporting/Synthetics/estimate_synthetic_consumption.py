import os
import requests
import time
import urllib.parse
import xlsxwriter

include_disabled = True
html_file_name = '../../$Output/Reporting/Synthetics/EstimatedSyntheticConsumption.html'
xlsx_file_name = '../../$Output/Reporting/Synthetics/EstimatedSyntheticConsumption.xlsx'


def process(env, token):
    row_count = 0
    rows = []
    endpoint = '/api/v1/synthetic/monitors'
    if include_disabled:
        params = ''
    else:
        raw_params = 'enabled=true'
        params = urllib.parse.quote(raw_params, safe='/,&=')
    synthetics_json_list = get_rest_api_json(env, token, endpoint, params)
    for synthetics_json in synthetics_json_list:
        inner_synthetics_json_list = synthetics_json.get('monitors')
        for inner_synthetics_json in inner_synthetics_json_list:
            # print(inner_synthetics_json)
            endpoint = '/api/v1/synthetic/monitors/' + inner_synthetics_json.get('entityId')
            synthetic_json = get_rest_api_json(env, token, endpoint, params)[0]
            # print(synthetic_json)
            synthetic_name = synthetic_json.get('name')
            synthetic_type = synthetic_json.get('type')
            synthetic_enabled = synthetic_json.get('enabled')
            synthetic_frequency = synthetic_json.get('frequencyMin')
            synthetic_locations = synthetic_json.get('locations')
            synthetic_location_count = len(synthetic_locations)
            if synthetic_enabled:
                synthetic_state = 'an enabled'
            else:
                synthetic_state = 'a disabled'
            if synthetic_type == 'BROWSER':
                synthetic_type = 'Browser'
                step_key = 'events'
            else:
                synthetic_type = 'HTTP'
                step_key = 'requests'
            script_events = synthetic_json.get('script').get(step_key)
            # for script_event in script_events:
            #     print(script_event)
            event_count = len(script_events)

            estimated_hourly_consumption = estimate_consumption(synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count)

            event_count_literal = 'steps'
            if event_count == 1:
                event_count_literal = 'step'
            synthetic_frequency_literal = 'minutes'
            if synthetic_frequency == 1:
                synthetic_frequency_literal = 'minute'
            synthetic_location_count_literal = 'locations'
            if synthetic_location_count == 1:
                synthetic_location_count_literal = 'location'
            estimated_hourly_consumption_literal = 'DEM Units'
            if estimated_hourly_consumption == 1:
                estimated_hourly_consumption_literal = 'DEM Unit'

            # Print a verbose summary of each Synthetic to the console
            print(f'{synthetic_name} is {synthetic_state} {synthetic_type} test with {event_count} {event_count_literal} scheduled to run every {synthetic_frequency} {synthetic_frequency_literal} from {synthetic_location_count} {synthetic_location_count_literal} for an estimated hourly consumption of {estimated_hourly_consumption} {estimated_hourly_consumption_literal}')

            # Save columns for each row to be output as HTML and XLSX
            row = (synthetic_name, synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count, estimated_hourly_consumption)
            rows.append(row)
            row_count += 1

            # For testing, stop at a small number of rows
            if row_count >= 50:
                break

        write_html(sorted(rows, key=lambda result: row[0].lower()))
        write_xlsx(sorted(rows, key=lambda result: row[0].lower()))


def estimate_consumption(synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count):
    # https://www.dynatrace.com/support/help/shortlink/digital-experience-monitoring-units#synthetic-actionsrequests-calculation-example
    if not synthetic_enabled:
        return 0

    hourly_frequency = 60/synthetic_frequency

    hourly_consumption = (event_count * hourly_frequency * synthetic_location_count)

    if synthetic_type == 'HTTP':
        hourly_consumption = hourly_consumption / 10

    return hourly_consumption


def write_xlsx(rows):
    # workbook = xlsxwriter.Workbook('../../$Output/Reporting/Synthetics/EstimatedSyntheticConsumption.xlsx')
    workbook = xlsxwriter.Workbook(xlsx_file_name)
    header_format = workbook.add_format({'bold': True, 'bg_color': '#B7C9E2'})

    worksheet = workbook.add_worksheet('Estimated Synthetic Consumption')

    row_index = 0
    column_index = 0

    headers = ['Synthetic Name', 'State (Enabled/Disabled)', 'Type (Browser/HTTP)', 'Number of Steps', 'Frequency (Runs every X minutes)', 'Number of Locations', 'Hourly DEM Unit Consumption']
    for _ in headers:
        worksheet.write(row_index, column_index, headers[column_index], header_format)
        column_index += 1
    row_index += 1

    for row in rows:
        synthetic_name, synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count, estimated_hourly_consumption = row
        worksheet.write(row_index, 0, synthetic_name)
        if synthetic_enabled:
            worksheet.write(row_index, 1, 'Enabled')
        else:
            worksheet.write(row_index, 1, 'Disabled')
        worksheet.write(row_index, 2, synthetic_type)
        worksheet.write(row_index, 3, event_count)
        worksheet.write(row_index, 4, synthetic_frequency)
        worksheet.write(row_index, 5, synthetic_location_count)
        worksheet.write(row_index, 6, estimated_hourly_consumption)
        row_index += 1

    worksheet.autofilter(0, 0, row_index, len(headers)) # add filter to all columns
    worksheet.autofit()
    workbook.close()


def write_html(rows):
    # filename = '../../$Output/Reporting/Synthetics/EstimatedSyntheticConsumption.html'

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

    headers = ['Synthetic Name', 'State', 'Type', 'Steps', 'Frequency', 'Locations', 'Estimated Consumption']

    table_header = '''    <table>
          <tr>
            <th>Synthetic Name</th>
            <th>State (Enabled/Disabled)</th>
            <th>Type (Browser/HTTP)</th>
            <th>Number of Steps</th>
            <th>Frequency (Runs every X minutes)</th>
            <th>Number of Locations</th>
            <th>Hourly DEM Unit Consumption</th>
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
        write_h1_heading(file, f'Estimated Synthetic Consumption')

        # Write Table Header
        write_line(file, table_header)

        # Write Table Rows
        for row in rows:
            synthetic_name, synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count, estimated_hourly_consumption = row
            if synthetic_enabled:
                synthetic_state = 'Enabled'
            else:
                synthetic_state = 'Disabled'
            write_line(file, f'{row_start}{col_start}{synthetic_name}{col_end}{col_start}{synthetic_state}{col_end}{col_start}{synthetic_type}{col_end}{col_start}{event_count}{col_end}{col_start}{synthetic_frequency}{col_end}{col_start}{synthetic_location_count}{col_end}{col_start}{estimated_hourly_consumption}{col_end}{row_end}')

        # Finish the HTML formatting
        write_line(file, html_bottom)


def write_h1_heading(outfile, heading):
    outfile.write('    <h1>' + heading + '</h1>')
    outfile.write('\n')


def write_line(outfile, content):
    outfile.write(content)
    outfile.write('\n')


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    try:
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token}, timeout=60.0)
    except (ConnectionError, TimeoutError):
        print('Sleeping 30 seconds before retrying due to connection or timeout error...')
        time.sleep(30)
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})

    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    json_data = resp.json()

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json_data) is list:
        # DEBUG:
        # print(json_data)
        return json_data

    json_list = [json_data]
    next_page_key = json_data.get('nextPageKey')

    while next_page_key is not None:
        # print(f'next_page_key: {next_page_key}')
        params = {'nextPageKey': next_page_key}
        full_url = url + endpoint
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
        # print(resp.url)

        if resp.status_code != 200:
            print('Paginated REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            exit(1)

        json_data = resp.json()
        # print(json_data)

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def main():
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

    print(f'Environment Name: {env_name}')
    print(f'Environment:      {env}')
    print(f'Token:            {masked_token}')

    print('')
    print('Estimate Synthetic Consumption')
    print(f'HTML report will be written to "{html_file_name}"')
    print(f'Excel report will be written to "{xlsx_file_name}"')
    process(env, token)


if __name__ == '__main__':
    main()
