import os
import requests

from inspect import currentframe
from json.decoder import JSONDecodeError

env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
# env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

tenant = os.environ.get(tenant_key)
token = os.environ.get(token_key)
env = f'https://{tenant}.live.dynatrace.com'


def get_rest_api_json(url, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    # print(f'Response Text {resp.text}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    try:
        json = resp.json()

        # Some json is just a list of dictionaries.
        # Config V1 AWS Credentials is the only example I am aware of.
        # For these, I have never seen pagination.
        if type(json) is list:
            # DEBUG:
            # print(json)
            return json

        json_list = [json]

        next_page_key = json.get('nextPageKey')

        while next_page_key is not None:
            # next_page_key = next_page_key.replace('=', '%3D') # Ths does NOT help.  Also, equals are apparently fine in params.
            # print(f'next_page_key: {next_page_key}')
            params = {'nextPageKey': next_page_key}
            full_url = url + endpoint
            resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
            # print(resp.url)

            if resp.status_code != 200:
                print('Paginated REST API Call Failed!')
                print(f'GET {full_url} {resp.status_code} - {resp.reason}')
                exit(1)

            json = resp.json()
            # print(json)

            next_page_key = json.get('nextPageKey')
            json_list.append(json)

        return json_list

    except JSONDecodeError:
        print('JSON decode error. Response: ')
        print(resp)
        print(resp.text)
        exit(get_line_number())


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def process():
    auto_tag_dict = {}

    endpoint = '/api/config/v1/autoTags'
    params = ''
    auto_tags_json_list = get_rest_api_json(env, endpoint, params)

    auto_tag_list = []
    for auto_tags_json in auto_tags_json_list:
        inner_auto_tags_json_list = auto_tags_json.get('values')
        for inner_auto_tags_json in inner_auto_tags_json_list:
            # entity_id = inner_auto_tags_json.get('id')
            name = inner_auto_tags_json.get('name')
            auto_tag_list.append(name)

    for auto_tag in sorted(auto_tag_list):
        # print(auto_tag)
        auto_tag_dict[auto_tag] = {'dashboards': [], 'managementZones': [], 'alertingProfiles': [], 'metricEvents': [], 'maintenanceWindows': []}

    # print('auto_tag_dict: ' +  str(auto_tag_dict))

    # print('')

    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboards_json_list = get_rest_api_json(env, endpoint, params)
    dashboard_id_list = []
    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')
            # name = inner_dashboards_json.get('name')
            dashboard_id_list.append(entity_id)
    for dashboard_id in sorted(dashboard_id_list):
        dashboard_json = get_rest_api_json(env, endpoint + '/' + dashboard_id, params)
        for dashboard in dashboard_json:
            dashboard_metadata = dashboard.get('dashboardMetadata')
            name = dashboard_metadata.get('name')
            # print(name)
            # print(dashboard)
            for auto_tag in sorted(auto_tag_list):
                if auto_tag in str(dashboard):
                    # print('Tag name (string) ' + auto_tag + ' found in dashboard ' + name)
                    try:
                        dashboard_list = auto_tag_dict[auto_tag].get('dashboards')
                        if name not in dashboard_list:
                            dashboard_list.append(name)
                            auto_tag_dict[auto_tag]['dashboards'] = dashboard_list
                    except KeyError:
                        print('Obsolete tag ' + auto_tag + ' referenced in dashboard ' + name)
    # print('')

    endpoint = '/api/config/v1/managementZones'
    params = ''
    management_zone_id_list = []
    management_zones_json_list = get_rest_api_json(env, endpoint, params)
    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        for inner_management_zones_json in inner_management_zones_json_list:
            entity_id = inner_management_zones_json.get('id')
            # name = inner_management_zones_json.get('name')
            management_zone_id_list.append(entity_id)
    for management_zone_id in sorted(management_zone_id_list):
        # print(management_zone_id)
        management_zone_json = get_rest_api_json(env, endpoint + '/' + management_zone_id, params)
        for management_zone in management_zone_json:
            # print(management_zone)
            rules = management_zone.get('rules')
            name = management_zone.get('name')
            for rule in rules:
                # print(rule)
                condition_list = rule.get('conditions')
                for condition in condition_list:
                    # print('condition: ' + str(condition))
                    comparison_info = condition.get('comparisonInfo')
                    comparison_info_type = comparison_info.get('type')
                    # print('comparison_info_type: ' + comparison_info_type)
                    if comparison_info_type == 'TAG':
                        comparison_info_value = comparison_info.get('value')
                        # print('comparison_info_value: ' + str(comparison_info_value))
                        comparison_info_value_key = comparison_info_value.get('key')
                        # print(comparison_info_value_key)
                        try:
                            management_zone_list = auto_tag_dict[comparison_info_value_key].get('managementZones')
                            # print(comparison_info_value_key + ' is used in management zone ' + name)
                            if name not in management_zone_list:
                                management_zone_list.append(name)
                                auto_tag_dict[comparison_info_value_key]['managementZones'] = management_zone_list
                        except KeyError:
                            print('Obsolete tag ' + comparison_info_value_key + ' referenced in management zone ' + name)

    # print('')

    endpoint = '/api/config/v1/alertingProfiles'
    params = ''
    alerting_profiles_json_list = get_rest_api_json(env, endpoint, params)
    alerting_profile_id_list = []
    for alerting_profiles_json in alerting_profiles_json_list:
        inner_alerting_profiles_json_list = alerting_profiles_json.get('values')
        for inner_alerting_profiles_json in inner_alerting_profiles_json_list:
            entity_id = inner_alerting_profiles_json.get('id')
            # name = inner_alerting_profiles_json.get('name')
            alerting_profile_id_list.append(entity_id)
    for alerting_profile_id in sorted(alerting_profile_id_list):
        # print(alerting_profile)
        alerting_profile_json = get_rest_api_json(env, endpoint + '/' + alerting_profile_id, params)
        for alerting_profile in alerting_profile_json:
            # print(alerting_profile)
            rules = alerting_profile.get('rules')
            display_name = alerting_profile.get('displayName')
            # print(rules)
            for rule in rules:
                tag_filters = rule.get('tagFilter').get('tagFilters')
                for tag_filter in tag_filters:
                    # print(tag_filter)
                    tag_filter_key = tag_filter.get('key')
                    if tag_filter_key in auto_tag_list:
                        try:
                            alerting_profile_list = auto_tag_dict[tag_filter_key].get('alertingProfiles')
                            # print(tag_filter_key + ' is used in alerting profile ' + display_name)
                            if display_name not in alerting_profile_list:
                                alerting_profile_list.append(display_name)
                                auto_tag_dict[tag_filter_key]['alertingProfiles'] = alerting_profile_list
                        except KeyError:
                            print('Obsolete tag ' + tag_filter_key + ' referenced in alerting profile ' + display_name)

    # print('')

    endpoint = '/api/config/v1/anomalyDetection/metricEvents'
    params = ''
    metric_event_id_list = []
    metric_events_json_list = get_rest_api_json(env, endpoint, params)
    # print('metric_events_json_list: ' + str(metric_events_json_list))
    for metric_events_json in metric_events_json_list:
        inner_metric_events_json_list = metric_events_json.get('values')
        for inner_metric_events_json in inner_metric_events_json_list:
            entity_id = inner_metric_events_json.get('id')
            # name = inner_metric_events_json.get('name')
            if not entity_id.startswith('ruxit') and not entity_id.startswith('dynatrace'):
                metric_event_id_list.append(entity_id)
    for metric_event_id in sorted(metric_event_id_list):
        # print(metric_event)
        metric_event_json = get_rest_api_json(env, endpoint + '/' + metric_event_id, params)
        for metric_event in metric_event_json:
            # print(metric_event)
            name = metric_event.get('name')
            alerting_scope_list = metric_event.get('alertingScope', [])
            for alerting_scope in alerting_scope_list:
                filter_type = alerting_scope.get('filterType')
                # print('filter_type: ' + filter_type)
                if filter_type == 'TAG':
                    tag_filter = alerting_scope.get('tagFilter')
                    if tag_filter:
                        tag_filter_key = tag_filter.get('key')
                        # print('tag_filter_key: ' +  tag_filter_key)
                        if tag_filter_key in auto_tag_list:
                            try:
                                metric_event_list = auto_tag_dict[tag_filter_key].get('metricEvents')
                                # print(tag_filter_key + ' is used in custom metric event ' + name)
                                if name not in metric_event_list:
                                    metric_event_list.append(name)
                                    auto_tag_dict[tag_filter_key]['metricEvents'] = metric_event_list
                            except KeyError:
                                print('Obsolete tag ' + tag_filter_key + ' referenced in custom metric event ' + name)

    endpoint = '/api/v2/settings/objects'
    params = 'schemaIds=builtin%3Aalerting.maintenance-window&fields=objectId%2Cvalue'
    settings_json_list = get_rest_api_json(env, endpoint, params)
    # print(settings_json_list)

    # schema_ids = []
    # schema_dict = {}

    for settings_json in settings_json_list:
        inner_settings_json_list = settings_json.get('items')
        # print(inner_settings_json_list)
        for inner_settings_json in inner_settings_json_list:
            # print(inner_settings_json)
            value = inner_settings_json.get('value')
            # print(value)
            name = value.get('generalProperties').get('name')
            maintenance_window_filters = value.get('filters')
            # print(maintenance_window_filters)
            for maintenance_window_filter in maintenance_window_filters:
                # print(maintenance_window_filter)
                entity_tags = maintenance_window_filter.get('entityTags', [])
                # print(entity_tags)
                tags = maintenance_window_filter.get('tags', [])
                # print(tags)
                tags.extend(entity_tags)
                # print(tags)
                # print(entity_tags)
                for tag in tags:
                    # print(tag)
                    # for key/value pairs, get the key only
                    if ':' in tag:
                        tag = tag.split(':')[0]
                    if tag in auto_tag_list:
                        try:
                            maintenance_window_list = auto_tag_dict[tag].get('maintenanceWindows')
                            # print(tag + ' is used in maintenance window ' + name)
                            if name not in maintenance_window_list:
                                maintenance_window_list.append(name)
                                auto_tag_dict[tag]['maintenanceWindows'] = maintenance_window_list
                        except KeyError:
                            print('Obsolete tag ' + tag + ' referenced in maintenance window ' + name)

    display_findings(auto_tag_dict)


def display_findings(auto_tag_dict):
    # print(auto_tag_dict)
    print('Findings:')
    keys = sorted(auto_tag_dict.keys())
    for key in keys:
        # print(key)
        auto_tag_xref = auto_tag_dict[key]
        # print(auto_tag_xref)
        auto_tag_xref_keys = auto_tag_xref.keys()
        for auto_tag_xref_key in auto_tag_xref_keys:
            # print(auto_tag_xref_key)
            if len(auto_tag_xref[auto_tag_xref_key]) > 0:
                print(key + ' used in ' + auto_tag_xref_key + ': ' + sort_and_stringify_list_items(auto_tag_xref[auto_tag_xref_key]))


def sort_and_stringify_list_items(any_list):
    list_str = str(sorted(any_list))
    list_str = list_str.replace('[', '')
    list_str = list_str.replace(']', '')
    list_str = list_str.replace("'", "")
    list_str = list_str.replace(' ', '')
    return list_str


if __name__ == '__main__':
    process()
