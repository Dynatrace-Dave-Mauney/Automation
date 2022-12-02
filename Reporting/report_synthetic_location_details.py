import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/synthetic/locations'
    params = 'type=PRIVATE'
    synthetic_locations_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)

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
            geo_location = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]

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
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, True)


if __name__ == '__main__':
    # print('Not to be run standalone.  Use one of the "perform_*.py" modules to run this module.')
    # exit(1)
    main()
