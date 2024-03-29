import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

entity_types_of_interest = [
    'APPLICATION',
    # 'CLOUD_APPLICATION',
    'CLOUD_APPLICATION_NAMESPACE',
    # 'CONTAINER_GROUP',
    'HOST',
    'KUBERNETES_CLUSTER',
    'KUBERNETES_NODE',
    'KUBERNETES_SERVICE',
    'PROCESS_GROUP',
    'SERVICE',
]

# For convenient testing
# entity_types_of_interest = [
#     'CONTAINER_GROUP',
# ]

openshift_admin_ignore_list = [
    'CLOUD_APPLICATION',
    'CONTAINER_GROUP',
    'PROCESS_GROUP',
]


def process(env, token):
    management_zone_lookup = get_management_zone_lookup(env, token)
    metric_event_lookup = get_metric_event_lookup(env, token)
    alerting_profile_lookup = get_alerting_profile_lookup(env, token)
    problem_notification_lookup = get_problem_notification_lookup(env, token)
    host_group_lookup = get_host_group_lookup(env, token)
    process_group_lookup = get_process_group_lookup(env, token)
    cloud_application_namespace_lookup = get_cloud_application_namespace_lookup(env, token)

    rows = []
    for entity_type in entity_types_of_interest:
        endpoint = '/api/v2/entities'
        entity_selector = 'type(' + entity_type + ')'
        raw_params = f'&entitySelector={entity_selector}&fields=managementZones,fromRelationships,toRelationships'
        if entity_type == 'HOST':
            raw_params += ',properties.MONITORINGMODE'
        if entity_type == 'SERVICE':
            raw_params += ',properties.serviceType'
        if entity_type == 'CONTAINER_GROUP':
            raw_params += ',properties.metadata'
        params = urllib.parse.quote(raw_params, safe='/,&=')
        entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
        for entities_json in entities_json_list:
            inner_entities_json_list = entities_json.get('entities')
            for inner_entities_json in inner_entities_json_list:
                # if entity_type == 'CONTAINER_GROUP':
                #     import json
                #     print(json.dumps(inner_entities_json, indent=4, sort_keys=False))
                entity_display_name = inner_entities_json.get('displayName')
                if entity_type.startswith('PROCESS_GROUP'):
                    # Skip the "Dynatrace Internal" process group/process group instances
                    if entity_display_name.startswith('Dynatrace') or entity_display_name.startswith('OneAgent') or entity_display_name.endswith(' System') or entity_display_name.startswith('Short-lived'):
                        continue

                host_group_name = ''
                process_group_name = ''
                monitoring_mode = ''
                cloud_application_namespace_name = ''
                alerting_profile_name = ''
                problem_notification_name = ''
                management_zone_list = inner_entities_json.get('managementZones')
                for management_zone in management_zone_list:
                    management_zone_name = management_zone.get('name')
                    management_zone_id = management_zone.get('id')

                    # Skip specified entity types for the OPENSHIFT_ADMIN management zone
                    if management_zone_name == 'OPENSHIFT_ADMIN' and entity_type in openshift_admin_ignore_list:
                        continue

                    alerting_profile_dict_list = alerting_profile_lookup.get(management_zone_id)

                    if alerting_profile_dict_list:
                        alerting_profile_name_list = []
                        alerting_profile_id_list = []
                        for alerting_profile_dict in alerting_profile_dict_list:
                            alerting_profile_name = alerting_profile_dict.get('name')
                            alerting_profile_id = alerting_profile_dict.get('id')
                            alerting_profile_name_list.append(alerting_profile_name)
                            alerting_profile_id_list.append(alerting_profile_id)

                        alerting_profile_name = report_writer.stringify_list(alerting_profile_name_list)

                        problem_notification_name_list = []
                        for alerting_profile_id in alerting_profile_id_list:
                            problem_notification_name = problem_notification_lookup.get(alerting_profile_id)
                            problem_notification_name_list.append(problem_notification_name)

                        problem_notification_name = report_writer.stringify_list(problem_notification_name_list)

                    entity_type_string = entity_type

                    if entity_type == 'SERVICE' and inner_entities_json.get('properties').get('serviceType') == 'DATABASE_SERVICE':
                        entity_type_string = 'DATABASE_SERVICE'

                    if entity_type == 'HOST':
                        properties = inner_entities_json.get('properties')
                        monitoring_mode = properties.get('monitoringMode')
                        from_relationship = inner_entities_json.get('fromRelationships', {})
                        is_instance_of_list = from_relationship.get('isInstanceOf', [])
                        for is_instance_of in is_instance_of_list:
                            instance_id = is_instance_of.get('id')
                            if instance_id.startswith('HOST_GROUP'):
                                host_group_name = host_group_lookup.get(instance_id, 'Not Found')

                    if entity_type == 'PROCESS_GROUP':
                        to_relationship = inner_entities_json.get('toRelationships', {})
                        is_host_group_of_list = to_relationship.get('isHostGroupOf', [])
                        for is_host_group_of in is_host_group_of_list:
                            host_group_id = is_host_group_of.get('id')
                            host_group_name = host_group_lookup.get(host_group_id, 'Not Found')

                    if entity_type == 'SERVICE':
                        from_relationship = inner_entities_json.get('fromRelationships', {})
                        runs_on_list = from_relationship.get('runsOn', [])
                        for runs_on in runs_on_list:
                            process_group_id = runs_on.get('id')
                            if process_group_id.startswith('PROCESS_GROUP'):
                                process_group_name = process_group_lookup.get(process_group_id, 'Not Found')

                    if entity_type == 'CLOUD_APPLICATION' or entity_type == 'KUBERNETES_SERVICE':
                        if entity_type == 'CLOUD_APPLICATION':
                            to_relationship_key = 'isNamespaceOfCa'
                        if entity_type == 'KUBERNETES_SERVICE':
                            to_relationship_key = 'isNamespaceOfKubernetesSvc'
                        to_relationship = inner_entities_json.get('toRelationships', {})
                        is_namespace_of_list = to_relationship.get(to_relationship_key, [])
                        for is_namespace_of in is_namespace_of_list:
                            cloud_application_namespace_id = is_namespace_of.get('id')
                            if cloud_application_namespace_id.startswith('CLOUD_APPLICATION_NAMESPACE'):
                                cloud_application_namespace_name = cloud_application_namespace_lookup.get(cloud_application_namespace_id)

                    if entity_type == 'CONTAINER_GROUP':
                        properties = inner_entities_json.get('properties', {})
                        meta_data_list = properties.get('metadata', [])
                        for meta_data in meta_data_list:
                            if 'KUBERNETES_NAMESPACE' in str(meta_data):
                                cloud_application_namespace_name = meta_data.get('value')
                                break

                    rows.append((management_zone_name, entity_type_string, entity_display_name, host_group_name, monitoring_mode, process_group_name, cloud_application_namespace_name, alerting_profile_name, problem_notification_name))

    for key in metric_event_lookup:
        metric_event_dict = metric_event_lookup.get(key)
        management_zone_id = metric_event_dict.get('managementZone')
        management_zone_name = management_zone_lookup.get(management_zone_id, 'UNKNOWN')
        summary = metric_event_dict.get('summary', 'UNKNOWN')
        rows.append((management_zone_name, 'Metric Event', summary, '', '', '', '', '', ''))

    rows = remove_duplicates(sorted(rows))

    report_writer.initialize_text_file(None)
    report_name = 'Management Zone Coverage Detail'
    report_headers = ['Management Zone', 'Entity Type', 'Entity Display Name', 'Host Group', 'Monitoring Mode', 'Process Group', 'Cloud Application Namespace', 'Alerting Profile', 'Problem Notification']
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=(0, len(report_headers) - 1))
    report_writer.write_html(None, report_name, report_headers, rows)


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


def get_host_group_lookup(env, token):
    host_group_lookup = {}
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST_GROUP)&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            host_group_lookup[entity_id] = display_name

    return host_group_lookup


def get_process_group_lookup(env, token):
    process_group_lookup = {}
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(PROCESS_GROUP)&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            process_group_lookup[entity_id] = display_name

    return process_group_lookup


def get_cloud_application_namespace_lookup(env, token):
    cloud_application_namespace_lookup = {}
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(CLOUD_APPLICATION_NAMESPACE)&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            cloud_application_namespace_lookup[entity_id] = display_name

    return cloud_application_namespace_lookup


def get_alerting_profile_lookup(env, token):
    alerting_profile_lookup = {}
    endpoint = '/api/config/v1/alertingProfiles'
    alerting_profiles_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    for alerting_profiles_json in alerting_profiles_json_list:
        inner_alerting_profiles_json_list = alerting_profiles_json.get('values')
        for inner_alerting_profiles_json in inner_alerting_profiles_json_list:
            entity_id = inner_alerting_profiles_json.get('id')
            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            alerting_profile = json.loads(r.text)
            # print(json.dumps(alerting_profile, indent=4, sort_keys=False))
            management_zone_id = alerting_profile.get('mzId')
            if management_zone_id:
                display_name = alerting_profile.get('displayName')
                alerting_profile_dict = {'name': display_name, 'id': entity_id}
                if management_zone_id in alerting_profile_lookup:
                    alerting_profile_lookup[management_zone_id].append(alerting_profile_dict)
                else:
                    alerting_profile_lookup[management_zone_id] = [alerting_profile_dict]

    return alerting_profile_lookup


def get_problem_notification_lookup(env, token):
    problem_notification_lookup = {}
    endpoint = '/api/config/v1/notifications'
    problem_notifications_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    for problem_notifications_json in problem_notifications_json_list:
        inner_problem_notifications_json_list = problem_notifications_json.get('values')
        for inner_problem_notifications_json in inner_problem_notifications_json_list:
            entity_id = inner_problem_notifications_json.get('id')
            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            problem_notification = json.loads(r.text)
            # print(json.dumps(problem_notification, indent=4, sort_keys=False))
            alerting_profile_id = problem_notification.get('alertingProfile')
            problem_notification_name = problem_notification.get('name')
            problem_notification_type = problem_notification.get('type', '')
            problem_notification_email_receivers = problem_notification.get('receivers')
            if problem_notification_type == 'EMAIL' and problem_notification_email_receivers:
                name_string = f'{problem_notification_name} (Email to {report_writer.stringify_list(problem_notification_email_receivers)})'
            else:
                name_string = problem_notification_name

            problem_notification_lookup[alerting_profile_id] = name_string

    return problem_notification_lookup


def get_metric_event_lookup(env, token):
    metric_event_lookup = {}

    endpoint = '/api/v2/settings/objects'
    schema_ids = 'builtin:anomaly-detection.metric-events'
    schema_ids_param = f'schemaIds={schema_ids}'
    raw_params = schema_ids_param + '&scopes=environment&fields=objectId,value,Summary&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for settings_object in settings_object_list:
        items = settings_object.get('items')
        for item in items:
            object_id = item.get('objectId')
            value = item.get('value')
            summary = value.get('summary')
            query_definition = value.get('queryDefinition', {})
            management_zone = query_definition.get('managementZone')
            # print(summary, management_zone, object_id)
            if management_zone:
                metric_event_lookup[object_id] = {'managementZone': management_zone, 'summary': summary}

    return metric_event_lookup


def get_management_zone_lookup(env, token):
    management_zone_lookup = {}
    endpoint = '/api/config/v1/managementZones'
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('values')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('id')
            name = inner_entities_json.get('name')
            management_zone_lookup[entity_id] = name

    return management_zone_lookup


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    _, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
