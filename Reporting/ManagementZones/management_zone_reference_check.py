import urllib.parse

from inspect import currentframe

from Reuse import dynatrace_api
from Reuse import environment

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


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def load_management_zone_lookup():
    management_zone_lookup = {}
    endpoint = '/api/config/v1/managementZones'
    params = ''
    management_zones_json_list = dynatrace_api.get(env, token, endpoint, params)
    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        for inner_management_zones_json in inner_management_zones_json_list:
            management_zone_name = inner_management_zones_json.get('name')
            management_zone_id = inner_management_zones_json.get('id')
            management_zone_lookup[management_zone_name] = management_zone_id

    return management_zone_lookup


def process():
    management_zone_dict = {}

    management_zone_lookup = load_management_zone_lookup()

    # Want to check every management zone?
    # It may take a while and I have not tested it yet.  I opted for hard coding a list to start.
    # endpoint = '/api/config/v1/managementZones'
    # params = ''
    # management_zones_json_list = dynatrace_api.get(env, token, endpoint, params)
    # management_zone_list = []
    # for management_zones_json in management_zones_json_list:
    #     inner_management_zones_json_list = management_zones_json.get('values')
    #     for inner_management_zones_json in inner_management_zones_json_list:
    #         # entity_id = inner_management_zones_json.get('id')
    #         name = inner_management_zones_json.get('name')
    #         management_zone_list.append(name)

    management_zone_list = []
    # management_zone_list = ['Readonly']

    if not management_zone_list:
        print('Please provide a list of management zone names to check for references in dashboards, alerting profiles, metric events and maintenance windows')
        print(f'This can be done at approximately line number {get_line_number() - 4}')
        exit(get_line_number())

    for management_zone in sorted(management_zone_list):
        management_zone_dict[management_zone] = {'dashboards': [], 'alertingProfiles': [], 'metricEvents': [], 'maintenanceWindows': []}

    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboards_json_list = dynatrace_api.get(env, token, endpoint, params)
    dashboard_id_list = []
    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')
            dashboard_id_list.append(entity_id)
    for dashboard_id in sorted(dashboard_id_list):
        dashboard_json = dynatrace_api.get(env, token, endpoint + '/' + dashboard_id, params)
        for dashboard in dashboard_json:
            dashboard_metadata = dashboard.get('dashboardMetadata')
            name = dashboard_metadata.get('name')
            for management_zone in sorted(management_zone_list):
                # The management zone name and id can appear at the dashboard or tile level, so search the dashboard as a string for simplicity.
                # It may result in false positives if the management zone name is "too common"
                if management_zone in str(dashboard):
                    try:
                        dashboard_list = management_zone_dict.get(management_zone).get('dashboards')
                        if name not in dashboard_list:
                            dashboard_list.append(name)
                            management_zone_dict[management_zone]['dashboards'] = dashboard_list
                    except KeyError:
                        print(f'Management zone {management_zone} referenced in dashboard {name} but no entry in management zone dictionary found')

    print('')

    endpoint = '/api/config/v1/alertingProfiles'
    params = ''
    alerting_profiles_json_list = dynatrace_api.get(env, token, endpoint, params)
    alerting_profile_id_list = []
    for alerting_profiles_json in alerting_profiles_json_list:
        inner_alerting_profiles_json_list = alerting_profiles_json.get('values')
        for inner_alerting_profiles_json in inner_alerting_profiles_json_list:
            entity_id = inner_alerting_profiles_json.get('id')
            alerting_profile_id_list.append(entity_id)
    for alerting_profile_id in sorted(alerting_profile_id_list):
        alerting_profile_json = dynatrace_api.get(env, token, endpoint + '/' + alerting_profile_id, params)
        for alerting_profile in alerting_profile_json:
            display_name = alerting_profile.get('displayName')
            management_zone_id = alerting_profile.get('managementZoneId')
            for management_zone in sorted(management_zone_list):
                if str(management_zone_id) == management_zone_lookup.get(management_zone):
                    try:
                        alerting_profile_list = management_zone_dict[str(management_zone)].get('alertingProfiles')
                        if display_name not in alerting_profile_list:
                            alerting_profile_list.append(display_name)
                            management_zone_dict[management_zone]['alertingProfiles'] = alerting_profile_list
                    except KeyError:
                        print(f'Management zone id {str(management_zone_id)} referenced in alerting profile {display_name} but no entry in management zone dictionary found for {management_zone}')

    print('')

    endpoint = '/api/v2/settings/objects'
    raw_params = 'schemaIds=builtin:alerting.maintenance-window&fields=objectId,value'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_json_list = dynatrace_api.get(env, token, endpoint, params)

    for settings_json in settings_json_list:
        inner_settings_json_list = settings_json.get('items')
        for inner_settings_json in inner_settings_json_list:
            value = inner_settings_json.get('value')
            name = value.get('generalProperties').get('name')
            maintenance_window_filters = value.get('filters')
            for maintenance_window_filter in maintenance_window_filters:
                management_zone_filters = maintenance_window_filter.get('managementZones', [])
                for management_zone_filter in management_zone_filters:
                    for management_zone in sorted(management_zone_list):
                        if management_zone_filter == management_zone_lookup.get(management_zone):
                            try:
                                maintenance_window_list = management_zone_dict[management_zone].get('maintenanceWindows')
                                if name not in maintenance_window_list:
                                    maintenance_window_list.append(name)
                                    management_zone_dict[management_zone]['maintenanceWindows'] = maintenance_window_list
                            except KeyError:
                                print(f'Management zone id {str(management_zone_filter)} referenced in maintenance window {name} but no entry in management zone dictionary found for {management_zone}')

    display_findings(management_zone_dict, management_zone_lookup)


def display_findings(management_zone_dict, management_zone_lookup):
    print('Findings:')
    keys = sorted(management_zone_dict.keys())
    for key in keys:
        management_zone_xref = management_zone_dict[key]
        management_zone_xref_keys = management_zone_xref.keys()
        for management_zone_xref_key in management_zone_xref_keys:
            if len(management_zone_xref[management_zone_xref_key]) > 0:
                management_zone_id = management_zone_lookup.get(key)
                print(f'{key} ({management_zone_id}) used in {management_zone_xref_key}: {sort_and_stringify_list_items(management_zone_xref.get(management_zone_xref_key))}')


def sort_and_stringify_list_items(any_list):
    list_str = str(sorted(any_list))
    list_str = list_str.replace('[', '')
    list_str = list_str.replace(']', '')
    list_str = list_str.replace("'", "")
    list_str = list_str.replace(' ', '')
    return list_str


if __name__ == '__main__':
    process()
