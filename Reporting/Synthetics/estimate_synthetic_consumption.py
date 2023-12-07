import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


include_disabled = True


def process(env, token):
    row_count = 0
    rows = []
    endpoint = '/api/v1/synthetic/monitors'
    if include_disabled:
        params = ''
    else:
        raw_params = 'enabled=true'
        params = urllib.parse.quote(raw_params, safe='/,&=')
    synthetics_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for synthetics_json in synthetics_json_list:
        inner_synthetics_json_list = synthetics_json.get('monitors')
        for inner_synthetics_json in inner_synthetics_json_list:
            endpoint = '/api/v1/synthetic/monitors/' + inner_synthetics_json.get('entityId')
            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
            synthetic_json = r.json()
            synthetic_name = synthetic_json.get('name')
            synthetic_type = synthetic_json.get('type')
            synthetic_enabled = synthetic_json.get('enabled')
            synthetic_frequency = synthetic_json.get('frequencyMin')
            synthetic_locations = synthetic_json.get('locations')
            synthetic_location_count = len(synthetic_locations)
            if synthetic_type == 'BROWSER':
                synthetic_type = 'Browser'
                step_key = 'events'
            else:
                synthetic_type = 'HTTP'
                step_key = 'requests'
            script_events = synthetic_json.get('script').get(step_key)
            event_count = len(script_events)

            estimated_hourly_consumption = estimate_consumption(synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count)

            row_data = (synthetic_name, synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count, estimated_hourly_consumption)
            rows.append(row_data)
            row_count += 1

            # For testing, stop at a small number of rows
            # if row_count >= 50:
            #     break

        sorted_rows = sorted(rows, key=lambda row: row[0].lower())

        report_name = 'Estimated Synthetic Consumption'
        report_headers = ['Synthetic Name', 'State (Enabled/Disabled)', 'Type (Browser/HTTP)', 'Number of Steps', 'Frequency (Runs every X minutes)', 'Number of Locations', 'Hourly DEM Unit Consumption']

        report_writer.write_console(report_name, report_headers, sorted_rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        report_writer.write_xlsx(None, report_name, report_headers, sorted_rows, header_format=None, auto_filter=(0, len(report_headers)))
        report_writer.write_html(None, report_name, report_headers, sorted_rows)


def estimate_consumption(synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count):
    # https://www.dynatrace.com/support/help/shortlink/digital-experience-monitoring-units#synthetic-actionsrequests-calculation-example
    if not synthetic_enabled:
        return 0

    if synthetic_frequency > 0:
        hourly_frequency = 60/synthetic_frequency
    else:
        hourly_frequency = 0

    hourly_consumption = (event_count * hourly_frequency * synthetic_location_count)

    if synthetic_type == 'HTTP':
        hourly_consumption = hourly_consumption / 10

    return hourly_consumption


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
    _, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)


if __name__ == '__main__':
    main()
