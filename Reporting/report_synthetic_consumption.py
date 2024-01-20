import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


include_disabled = True


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []

    count_total = 0
    count_too_many_dem_units = 0
    count_total_dem_units_per_hour = 0
    maximum_dem_units_per_hour = 0
    average_dem_units_per_hour = 0

    too_many_dem_units_threshold = 120

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
            count_total_dem_units_per_hour += estimated_hourly_consumption
            if estimated_hourly_consumption > maximum_dem_units_per_hour:
                maximum_dem_units_per_hour = estimated_hourly_consumption

            if not summary_mode:
                row_data = (synthetic_name, synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count, estimated_hourly_consumption)
                rows.append(row_data)

            count_total += 1

            if estimated_hourly_consumption > too_many_dem_units_threshold:
                count_too_many_dem_units += 1

            # For testing, stop at a small number of rows
            # if count_total >= 50:
            #     break

        if count_total > 0:
            average_dem_units_per_hour = count_total_dem_units_per_hour / count_total
        else:
            average_dem_units_per_hour = 0

        summary.append(f'There are {count_total} synthetic tests currently defined.')
        summary.append(f'There are {count_too_many_dem_units} synthetic tests currently defined using more than {too_many_dem_units_threshold} DEM units per hour.')
        summary.append(f'There are {count_total_dem_units_per_hour} total DEM units per hour being consumed by Synthetics.')
        summary.append(f'The maximum consumption by a Synthetic is {maximum_dem_units_per_hour} DEM units per hour.')
        summary.append(f'The average consumption by all Synthetics is {average_dem_units_per_hour} DEM units per hour.')

        if not summary_mode:
            sorted_rows = sorted(rows, key=lambda row: row[0].lower())
            report_name = 'Estimated Synthetic Consumption'
            report_headers = ['Synthetic Name', 'State (Enabled/Disabled)', 'Type (Browser/HTTP)', 'Number of Steps', 'Frequency (Runs every X minutes)', 'Number of Locations', 'Hourly DEM Unit Consumption']
            report_writer.write_console(report_name, report_headers, sorted_rows, delimiter='|')
            report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
            write_string(f'Total Synthetic Tests: {count_total}')
            write_string(f'Synthetics using more than {too_many_dem_units_threshold} DEM units per hour: {count_too_many_dem_units}')
            write_string(f'Total DEM units per hour being consumed by Synthetics: {count_total_dem_units_per_hour}')
            write_string(f'Maximum DEM units per hour consumption by a Synthetic: {maximum_dem_units_per_hour}')
            write_string(f'Average DEM units per hour consumption by all Synthetics: {average_dem_units_per_hour}')
            write_strings(summary)
            report_writer.write_xlsx(None, report_name, report_headers, sorted_rows, header_format=None, auto_filter=(0, len(report_headers)))
            report_writer.write_html(None, report_name, report_headers, sorted_rows)

    return summary


def write_string(string):
    report_writer.write_console_plain_text([string])
    report_writer.write_plain_text(None, [string])


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


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
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    _, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)
    # print(summarize(env, token))


if __name__ == '__main__':
    main()
