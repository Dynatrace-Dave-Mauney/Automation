import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []

    count_total = 0
    count_rum_enabled = 0
    count_rum_disabled = 0
    count_session_replay_enabled = 0
    count_session_replay_disabled = 0
    count_xhr_enabled = 0
    count_xhr_disabled = 0
    count_with_monitors = 0
    count_without_monitors = 0
    count_with_user_tags = 0
    count_without_user_tags = 0
    count_with_conversion_goals = 0
    count_without_conversion_goals = 0

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(APPLICATION)&fields=+properties&from=-5y'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')

            # My Web Application/Default Application ID
            if entity_id == 'APPLICATION-EA7C4B59F27D43EB':
                continue

            # if 'PRD' not in display_name.upper():
            #     continue

            # if entity_id == 'APPLICATION-00107DC9B083370D':
            #     import json
            #     formatted_json = json.dumps(inner_entities_json, indent=4, sort_keys=False)
            #     print(formatted_json)
            #     r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            #     application_json = r.json()
            #     formatted_json = json.dumps(application_json, indent=4, sort_keys=False)
            #     print(formatted_json)
            #     to_relationships = application_json.get('toRelationships')
            #     monitors = to_relationships.get('monitors')
            #     r = dynatrace_api.get_without_pagination(f'{env}/api/config/v1/applications/web/{entity_id}', token)
            #     application_json = r.json()
            #     formatted_json = json.dumps(application_json, indent=4, sort_keys=False)
            #     print(formatted_json)
            #     print('monitors: ', monitors)
            #
            #     exit(1111)

            properties = inner_entities_json.get('properties')
            detected_name = properties.get('detectedName', '')
            application_type = properties.get('applicationType', '')
            application_injection_type = properties.get('applicationInjectionType', '')
            rule_applied_match_type = properties.get('ruleAppliedMatchType', '')
            application_match_target = properties.get('applicationMatchTarget', '')
            rule_applied_pattern = properties.get('ruleAppliedPattern', '')
            customized_name = properties.get('customizedName', '')

            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            web_application_json = r.json()
            to_relationships = web_application_json.get('toRelationships')
            monitors = to_relationships.get('monitors')
            if monitors:
                count_with_monitors += 1
                synthetic_integration = 'True'
            else:
                count_without_monitors += 1
                synthetic_integration = 'False'

            r = dynatrace_api.get_without_pagination(f'{env}/api/config/v1/applications/web/{entity_id}', token)
            web_application_config_json = r.json()
            real_user_monitoring_enabled = web_application_config_json.get('realUserMonitoringEnabled')
            cost_control_user_session_percentage = web_application_config_json.get('costControlUserSessionPercentage')
            session_replay_config = web_application_config_json.get('sessionReplayConfig')
            session_replay_enabled = session_replay_config.get('enabled')
            session_replay_cost_control_percentage = session_replay_config.get('costControlPercentage')
            monitoring_settings = web_application_config_json.get('monitoringSettings')
            monitoring_settings_fetch_requests = monitoring_settings.get('fetchRequests')
            monitoring_settings_xml_http_request = monitoring_settings.get('xmlHttpRequest')
            monitoring_settings_java_script_framework_support = monitoring_settings.get('javaScriptFrameworkSupport')
            monitoring_settings_java_script_framework_support_angular = monitoring_settings_java_script_framework_support.get('angular')
            monitoring_settings_java_script_framework_support_dojo = monitoring_settings_java_script_framework_support.get('dojo')
            monitoring_settings_java_script_framework_support_extjs = monitoring_settings_java_script_framework_support.get('extJS')
            monitoring_settings_java_script_framework_support_icefaces = monitoring_settings_java_script_framework_support.get('icefaces')
            monitoring_settings_java_script_framework_support_jquery = monitoring_settings_java_script_framework_support.get('jQuery')
            monitoring_settings_java_script_framework_support_moo_tools = monitoring_settings_java_script_framework_support.get('mooTools')
            monitoring_settings_java_script_framework_support_prototype = monitoring_settings_java_script_framework_support.get('prototype')
            monitoring_settings_java_script_framework_support_activex_object = monitoring_settings_java_script_framework_support.get('activeXObject')

            user_tags = web_application_config_json.get('userTags')
            if user_tags:
                count_with_user_tags += 1
                user_tag_captured = 'True'
            else:
                count_without_user_tags += 1
                user_tag_captured = 'False'

            conversion_goals = web_application_config_json.get('conversionGoals')
            if conversion_goals:
                count_with_conversion_goals += 1
                conversion_goal_captured = 'True'
            else:
                count_without_conversion_goals += 1
                conversion_goal_captured = 'False'

            if not summary_mode:
                rows.append((display_name, customized_name, detected_name, entity_id, application_type, application_injection_type, real_user_monitoring_enabled, cost_control_user_session_percentage, session_replay_enabled, session_replay_cost_control_percentage, monitoring_settings_fetch_requests, monitoring_settings_xml_http_request, monitoring_settings_java_script_framework_support_angular, monitoring_settings_java_script_framework_support_dojo, monitoring_settings_java_script_framework_support_extjs, monitoring_settings_java_script_framework_support_icefaces, monitoring_settings_java_script_framework_support_jquery, monitoring_settings_java_script_framework_support_moo_tools, monitoring_settings_java_script_framework_support_prototype, monitoring_settings_java_script_framework_support_activex_object, synthetic_integration, user_tag_captured, rule_applied_match_type, application_match_target, rule_applied_pattern))

            count_total += 1

            if real_user_monitoring_enabled:
                count_rum_enabled += 1
            else:
                count_rum_disabled += 1

            if session_replay_enabled:
                count_session_replay_enabled += 1
            else:
                count_session_replay_disabled += 1

            if monitoring_settings_fetch_requests or monitoring_settings_xml_http_request or monitoring_settings_java_script_framework_support_angular or monitoring_settings_java_script_framework_support_dojo or monitoring_settings_java_script_framework_support_extjs or monitoring_settings_java_script_framework_support_icefaces or monitoring_settings_java_script_framework_support_jquery or monitoring_settings_java_script_framework_support_moo_tools or monitoring_settings_java_script_framework_support_prototype or monitoring_settings_java_script_framework_support_activex_object:
                count_xhr_enabled += 1
            else:
                count_xhr_disabled += 1

    summary.append(f'There are {count_total} web applications currently defined and reporting data.')
    summary.append(f'There are {count_rum_enabled} web applications currently defined and reporting data with RUM enabled.')
    summary.append(f'There are {count_rum_disabled} web applications currently defined and reporting data with RUM disabled.')
    summary.append(f'There are {count_session_replay_enabled} web applications currently defined and reporting data with session replay enabled.')
    summary.append(f'There are {count_session_replay_disabled} web applications currently defined and reporting data with session replay disabled.')
    summary.append(f'There are {count_xhr_enabled} web applications currently defined and reporting data with session XHR capturing enabled.')
    summary.append(f'There are {count_xhr_disabled} web applications currently defined and reporting data with session XHR capturing disabled.')
    summary.append(f'There are {count_with_monitors} web applications currently defined and reporting data with synthetic integration.')
    summary.append(f'There are {count_without_monitors} web applications currently defined and reporting data without synthetic integration.')
    summary.append(f'There are {count_with_user_tags} web applications currently defined and reporting data with user tag capture configured.')
    summary.append(f'There are {count_without_user_tags} web applications currently defined and reporting data without user tag capture configured.')
    summary.append(f'There are {count_with_conversion_goals} web applications currently defined and reporting data with conversion goal(s) configured.')
    summary.append(f'There are {count_without_conversion_goals} web applications currently defined and reporting data without conversion goal(s) configured.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Applications'
        report_writer.initialize_text_file(None)
        report_headers = ('Display Name', 'Customized Name', 'Detected Name', 'Entity ID', 'Application Type', 'Application Injection Type', 'RUM Enabled', 'RUM User Session Percentage', 'Session Replay Enabled', 'Session Replay Percentage', 'JS: Fetch Requests', 'JS: XML HTTP Request', 'JS: Angular', 'JS: Dojo', 'JS: extJS', 'JS: icefaces', 'JS: jQuery', 'JS: mooTools', 'JS: prototype', 'JS: activeXObject', 'Synthetic Integration', 'User Tag Configuration', 'Rule Applied Match Type', 'Application Match Target', 'Rule Applied Pattern')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_string(f'Total applications: {count_total}')
        write_string(f'RUM Enabled: {count_rum_enabled}')
        write_string(f'RUM Disabled: {count_rum_disabled}')
        write_string(f'Session Replay Enabled: {count_session_replay_enabled}')
        write_string(f'Session Replay Disabled: {count_session_replay_disabled}')
        write_string(f'XHR Enabled: {count_xhr_enabled}')
        write_string(f'XHR Disabled: {count_xhr_disabled}')
        write_string(f'With Synthetic Integration: {count_with_monitors}')
        write_string(f'Without Synthetic Integration: {count_without_monitors}')
        write_string(f'With User Tag Capture Configured: {count_with_user_tags}')
        write_string(f'Without User Tag Capture Configured: {count_without_user_tags}')
        write_string(f'With Conversion Goals Configured: {count_with_conversion_goals}')
        write_string(f'Without Conversion Goals Configured: {count_without_conversion_goals}')
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_string(string):
    report_writer.write_console_plain_text([string])
    report_writer.write_plain_text(None, [string])


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    env_name_supplied = 'Prod'
    env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
