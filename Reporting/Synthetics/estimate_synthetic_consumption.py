import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


include_disabled = True


def process(env_name, env, token):
    html_file_name = f'../../$Output/Reporting/Synthetics/{env_name}/EstimatedSyntheticConsumption.html'
    xlsx_file_name = f'../../$Output/Reporting/Synthetics/{env_name}/EstimatedSyntheticConsumption.xlsx'

    print(f'HTML report will be written to "{html_file_name}"')
    print(f'Excel report will be written to "{xlsx_file_name}"')

    row_count = 0
    rows = []
    endpoint = '/api/v1/synthetic/monitors'
    if include_disabled:
        params = ''
    else:
        raw_params = 'enabled=true'
        params = urllib.parse.quote(raw_params, safe='/,&=')
    synthetics_json_list = dynatrace_api.get(env, token, endpoint, params)
    for synthetics_json in synthetics_json_list:
        inner_synthetics_json_list = synthetics_json.get('monitors')
        for inner_synthetics_json in inner_synthetics_json_list:
            endpoint = '/api/v1/synthetic/monitors/' + inner_synthetics_json.get('entityId')
            synthetic_json = dynatrace_api.get(env, token, endpoint, params)[0]
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
            # print(f'{synthetic_name} is {synthetic_state} {synthetic_type} test with {event_count} {event_count_literal} scheduled to run every {synthetic_frequency} {synthetic_frequency_literal} from {synthetic_location_count} {synthetic_location_count_literal} for an estimated hourly consumption of {estimated_hourly_consumption} {estimated_hourly_consumption_literal}')

            row_data = (synthetic_name, synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count, estimated_hourly_consumption)
            rows.append(row_data)
            row_count += 1

            # For testing, stop at a small number of rows
            if row_count >= 50:
                break

        write_console(sorted(rows, key=lambda row: row[0].lower()))
        write_html(html_file_name, sorted(rows, key=lambda row: row[0].lower()))
        write_xlsx(xlsx_file_name, sorted(rows, key=lambda row: row[0].lower()))


def estimate_consumption(synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count):
    # https://www.dynatrace.com/support/help/shortlink/digital-experience-monitoring-units#synthetic-actionsrequests-calculation-example
    if not synthetic_enabled:
        return 0

    hourly_frequency = 60/synthetic_frequency

    hourly_consumption = (event_count * hourly_frequency * synthetic_location_count)

    if synthetic_type == 'HTTP':
        hourly_consumption = hourly_consumption / 10

    return hourly_consumption


def write_console(rows):
    title = 'Estimated Synthetic Consumption'
    headers = ['Synthetic Name', 'State (Enabled/Disabled)', 'Type (Browser/HTTP)', 'Number of Steps', 'Frequency (Runs every X minutes)', 'Number of Locations', 'Hourly DEM Unit Consumption']
    delimiter = '|'
    report_writer.write_console(title, headers, rows, delimiter)


def write_xlsx(xlsx_file_name, rows):
    worksheet_name = 'Estimated Synthetic Consumption'
    headers = ['Synthetic Name', 'State (Enabled/Disabled)', 'Type (Browser/HTTP)', 'Number of Steps', 'Frequency (Runs every X minutes)', 'Number of Locations', 'Hourly DEM Unit Consumption']
    header_format = None
    auto_filter = (0, len(headers))
    report_writer.write_xlsx(xlsx_file_name, worksheet_name, headers, rows, header_format, auto_filter)


def write_html(html_file_name, rows):
    page_heading = 'Estimated Synthetic Consumption'
    table_headers = ['Synthetic Name', 'State (Enabled/Disabled)', 'Type (Browser/HTTP)', 'Number of Steps', 'Frequency (Runs every X minutes)', 'Number of Locations', 'Hourly DEM Unit Consumption']
    report_writer.write_html(html_file_name, page_heading, table_headers, rows)


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

    process(env_name, env, token)


if __name__ == '__main__':
    main()
