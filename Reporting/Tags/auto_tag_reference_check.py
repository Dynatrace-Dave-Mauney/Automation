import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []
    auto_tag_dict = {}

    endpoint = '/api/config/v1/autoTags'
    params = ''
    auto_tags_json_list = dynatrace_api.get(env, token, endpoint, params)

    auto_tag_list = []
    for auto_tags_json in auto_tags_json_list:
        inner_auto_tags_json_list = auto_tags_json.get('values')
        for inner_auto_tags_json in inner_auto_tags_json_list:
            name = inner_auto_tags_json.get('name')
            auto_tag_list.append(name)

    for auto_tag in sorted(auto_tag_list):
        auto_tag_dict[auto_tag] = {'dashboards': [], 'managementZones': [], 'alertingProfiles': [], 'metricEvents': [], 'maintenanceWindows': []}

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
            for auto_tag in sorted(auto_tag_list):
                if auto_tag in str(dashboard):
                    try:
                        dashboard_list = auto_tag_dict[auto_tag].get('dashboards')
                        if name not in dashboard_list:
                            dashboard_list.append(name)
                            auto_tag_dict[auto_tag]['dashboards'] = dashboard_list
                    except KeyError:
                        rows.append(['Obsolete tag ' + auto_tag + ' referenced in dashboard ' + name])

    endpoint = '/api/config/v1/managementZones'
    params = ''
    management_zone_id_list = []
    management_zones_json_list = dynatrace_api.get(env, token, endpoint, params)
    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        for inner_management_zones_json in inner_management_zones_json_list:
            entity_id = inner_management_zones_json.get('id')
            management_zone_id_list.append(entity_id)
    for management_zone_id in sorted(management_zone_id_list):
        management_zone_json = dynatrace_api.get(env, token, endpoint + '/' + management_zone_id, params)
        for management_zone in management_zone_json:
            rules = management_zone.get('rules')
            name = management_zone.get('name')
            for rule in rules:
                condition_list = rule.get('conditions')
                for condition in condition_list:
                    comparison_info = condition.get('comparisonInfo')
                    comparison_info_type = comparison_info.get('type')
                    if comparison_info_type == 'TAG':
                        comparison_info_value = comparison_info.get('value')
                        comparison_info_value_key = comparison_info_value.get('key')
                        try:
                            management_zone_list = auto_tag_dict[comparison_info_value_key].get('managementZones')
                            if name not in management_zone_list:
                                management_zone_list.append(name)
                                auto_tag_dict[comparison_info_value_key]['managementZones'] = management_zone_list
                        except KeyError:
                            rows.append(['Obsolete tag ' + comparison_info_value_key + ' referenced in management zone ' + name])

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
            rules = alerting_profile.get('rules')
            display_name = alerting_profile.get('displayName')
            for rule in rules:
                tag_filters = rule.get('tagFilter').get('tagFilters')
                for tag_filter in tag_filters:
                    tag_filter_key = tag_filter.get('key')
                    if tag_filter_key in auto_tag_list:
                        try:
                            alerting_profile_list = auto_tag_dict[tag_filter_key].get('alertingProfiles')
                            if display_name not in alerting_profile_list:
                                alerting_profile_list.append(display_name)
                                auto_tag_dict[tag_filter_key]['alertingProfiles'] = alerting_profile_list
                        except KeyError:
                            rows.append(['Obsolete tag ' + tag_filter_key + ' referenced in alerting profile ' + display_name])

    endpoint = '/api/config/v1/anomalyDetection/metricEvents'
    params = ''
    metric_event_id_list = []
    metric_events_json_list = dynatrace_api.get(env, token, endpoint, params)
    for metric_events_json in metric_events_json_list:
        inner_metric_events_json_list = metric_events_json.get('values')
        for inner_metric_events_json in inner_metric_events_json_list:
            entity_id = inner_metric_events_json.get('id')
            if not entity_id.startswith('ruxit') and not entity_id.startswith('dynatrace'):
                metric_event_id_list.append(entity_id)
    for metric_event_id in sorted(metric_event_id_list):
        metric_event_json = dynatrace_api.get(env, token, endpoint + '/' + metric_event_id, params)
        for metric_event in metric_event_json:
            name = metric_event.get('name')
            alerting_scope_list = metric_event.get('alertingScope', [])
            for alerting_scope in alerting_scope_list:
                filter_type = alerting_scope.get('filterType')
                if filter_type == 'TAG':
                    tag_filter = alerting_scope.get('tagFilter')
                    if tag_filter:
                        tag_filter_key = tag_filter.get('key')
                        if tag_filter_key in auto_tag_list:
                            try:
                                metric_event_list = auto_tag_dict[tag_filter_key].get('metricEvents')
                                if name not in metric_event_list:
                                    metric_event_list.append(name)
                                    auto_tag_dict[tag_filter_key]['metricEvents'] = metric_event_list
                            except KeyError:
                                rows.append(['Obsolete tag ' + tag_filter_key + ' referenced in custom metric event ' + name])

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
                entity_tags = maintenance_window_filter.get('entityTags', [])
                tags = maintenance_window_filter.get('tags', [])
                tags.extend(entity_tags)
                for tag in tags:
                    if ':' in tag:
                        tag = tag.split(':')[0]
                    if tag in auto_tag_list:
                        try:
                            maintenance_window_list = auto_tag_dict[tag].get('maintenanceWindows')
                            if name not in maintenance_window_list:
                                maintenance_window_list.append(name)
                                auto_tag_dict[tag]['maintenanceWindows'] = maintenance_window_list
                        except KeyError:
                            rows.append(['Obsolete tag ' + tag + ' referenced in maintenance window ' + name])

    compile_findings(auto_tag_dict, rows)

    report_name = 'Auto Tag References'
    report_writer.initialize_text_file(None)
    report_headers = ['Finding']
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def compile_findings(auto_tag_dict, rows):
    print('Findings:')
    keys = sorted(auto_tag_dict.keys())
    for key in keys:
        auto_tag_xref = auto_tag_dict[key]
        auto_tag_xref_keys = auto_tag_xref.keys()
        for auto_tag_xref_key in auto_tag_xref_keys:
            if len(auto_tag_xref[auto_tag_xref_key]) > 0:
                rows.append([key + ' used in ' + auto_tag_xref_key + ': ' + sort_and_stringify_list_items(auto_tag_xref[auto_tag_xref_key])])


def sort_and_stringify_list_items(any_list):
    list_str = str(sorted(any_list))
    list_str = list_str.replace('[', '')
    list_str = list_str.replace(']', '')
    list_str = list_str.replace("'", "")
    list_str = list_str.replace(' ', '')
    return list_str


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

    process(env, token)


if __name__ == '__main__':
    main()
