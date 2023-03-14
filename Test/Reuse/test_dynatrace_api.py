import sys

# Support import from "Reuse" package when invoked from command line
# sys.path.append("../..")

from Reuse import environment
from Reuse import dynatrace_api


def test_get():
    env, token = environment.get_environment('Dev')
    endpoint = '/api/v1/synthetic/monitors'
    params = ''
    synthetics_json_list = dynatrace_api.get(env, token, endpoint, params)
    for synthetics_json in synthetics_json_list:
        inner_synthetics_json_list = synthetics_json.get('monitors')
        for inner_synthetics_json in inner_synthetics_json_list:
            # print(inner_synthetics_json)
            endpoint = '/api/v1/synthetic/monitors/' + inner_synthetics_json.get('entityId')
            synthetic_json = dynatrace_api.get(env, token, endpoint, params)[0]
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

            estimated_hourly_consumption = estimate_consumption(synthetic_enabled, synthetic_type, event_count,
                                                                synthetic_frequency, synthetic_location_count)

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

            print(f'{synthetic_name} is {synthetic_state} {synthetic_type} test with {event_count} {event_count_literal} scheduled to run every {synthetic_frequency} {synthetic_frequency_literal} from {synthetic_location_count} {synthetic_location_count_literal} for an estimated hourly consumption of {estimated_hourly_consumption} {estimated_hourly_consumption_literal}')


def estimate_consumption(synthetic_enabled, synthetic_type, event_count, synthetic_frequency, synthetic_location_count):
    # https://www.dynatrace.com/support/help/shortlink/digital-experience-monitoring-units#synthetic-actionsrequests-calculation-example
    if not synthetic_enabled:
        return 0

    hourly_frequency = 60/synthetic_frequency

    hourly_consumption = (event_count * hourly_frequency * synthetic_location_count)

    if synthetic_type == 'HTTP':
        hourly_consumption = hourly_consumption / 10

    return hourly_consumption


if __name__ == '__main__':
    test_get()
