from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/synthetic/locations'
    params = 'type=PRIVATE'
    synthetic_locations_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('name' + '|' + 'entityId' + '|' + 'type' + '|' + 'status' + '|' + 'geoLocationId' + '|' +
              'countryCode' + '|' + 'regionCode' + '|' + 'city' + '|' + 'latitude' + '|' + 'longitude' + '|' +
              'status' + '|' + 'availabilityLocationOutage' + '|' + 'availabilityNodeOutage' + '|' +
              'locationNodeOutageDelayInMinutes' + '|' + 'availabilityNotificationsEnabled' + '|' + 'autoUpdateChromium')

    for synthetic_locations_json in synthetic_locations_json_list:
        inner_synthetic_locations_json_list = synthetic_locations_json.get('locations')
        for inner_synthetic_locations_json in inner_synthetic_locations_json_list:
            name = inner_synthetic_locations_json.get('name')
            entity_id = inner_synthetic_locations_json.get('entityId')
            entity_type = inner_synthetic_locations_json.get('type')
            status = inner_synthetic_locations_json.get('status')
            geo_location_id = inner_synthetic_locations_json.get('geoLocationId')

            endpoint = '/api/v2/synthetic/locations/' + geo_location_id
            params = ''
            geo_location = dynatrace_api.get(env, token, endpoint, params)[0]

            # DEBUG:
            # print(geo_location)

            geo_country_code = geo_location.get('countryCode')
            geo_region_code = geo_location.get('regionCode')
            geo_city = geo_location.get('city')
            geo_latitude = geo_location.get('latitude')
            geo_longitude = geo_location.get('longitude')
            geo_status = geo_location.get('status')
            geo_availability_location_outage = geo_location.get('availabilityLocationOutage')
            geo_availability_node_outage = geo_location.get('availabilityNodeOutage')
            geo_location_node_outage_delay_in_minutes = geo_location.get('locationNodeOutageDelayInMinutes')
            geo_availability_notifications_enabled = geo_location.get('availabilityNotificationsEnabled')
            geo_auto_update_chromium = geo_location.get('autoUpdateChromium')

            if print_mode:
                print(name + '|' + entity_id + '|' + entity_type + '|' + status + '|' + geo_location_id + '|' +
                      geo_country_code + '|' + geo_region_code + '|' + geo_city + '|' + str(geo_latitude) + '|' +
                      str(geo_longitude) + '|' + geo_status + '|' + str(geo_availability_location_outage) + '|' +
                      str(geo_availability_node_outage) + '|' + str(geo_location_node_outage_delay_in_minutes) + '|' +
                      str(geo_availability_notifications_enabled) + '|' + str(geo_auto_update_chromium))

            count_total += 1

    if print_mode:
        print('Total Synthetic Locations: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' synthetic locations currently defined and reporting.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)
        

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
    process(env, token, True)
    
    
if __name__ == '__main__':
    main()
