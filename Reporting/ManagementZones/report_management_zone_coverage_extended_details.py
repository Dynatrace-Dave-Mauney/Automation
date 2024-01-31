import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

entity_types_of_interest = [
    'APPLICATION',
    'CLOUD_APPLICATION',
    'CLOUD_APPLICATION_NAMESPACE',
    'CONTAINER_GROUP',
    'HOST',
    'KUBERNETES_CLUSTER',
    'KUBERNETES_NODE',
    'KUBERNETES_SERVICE',
    'PROCESS_GROUP',
    'SERVICE',
]

openshift_admin_ignore_list = [
    'CLOUD_APPLICATION',
    'CONTAINER_GROUP',
    'PROCESS_GROUP',
]


def process(env, token):
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
        params = urllib.parse.quote(raw_params, safe='/,&=')
        entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
        for entities_json in entities_json_list:
            inner_entities_json_list = entities_json.get('entities')
            for inner_entities_json in inner_entities_json_list:
                # print(json.dumps(inner_entities_json, indent=4, sort_keys=False))
                entity_display_name = inner_entities_json.get('displayName')
                if entity_type.startswith('PROCESS_GROUP'):
                    # Skip the "Dynatrace Internal" process group/process group instances
                    if entity_display_name.startswith('Dynatrace') or entity_display_name.startswith('OneAgent') or entity_display_name.endswith(' System') or entity_display_name.startswith('Short-lived'):
                        continue

                host_group_name = ''
                process_group_name = ''
                monitoring_mode = ''
                cloud_application_namespace_name = ''
                management_zone_list = inner_entities_json.get('managementZones')
                for management_zone in management_zone_list:
                    management_zone_name = management_zone.get('name')
                    if entity_type == 'SERVICE' and inner_entities_json.get('properties').get('serviceType') == 'DATABASE_SERVICE':
                        rows.append((management_zone_name, 'DATABASE_SERVICE', entity_display_name, host_group_name, monitoring_mode, process_group_name, cloud_application_namespace_name))
                    else:
                        if management_zone_name == 'OPENSHIFT_ADMIN' and entity_type in openshift_admin_ignore_list:
                            continue
                        else:
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
                            rows.append((management_zone_name, entity_type, entity_display_name, host_group_name, monitoring_mode, process_group_name, cloud_application_namespace_name))

    rows = remove_duplicates(sorted(rows))

    report_writer.initialize_text_file(None)
    report_name = 'Management Zone Coverage Detail'
    report_headers = ['Management Zone', 'Entity Type', 'Entity Display Name', 'Host Group', 'Monitoring Mode', 'Process Group', 'Cloud Application Namespace']
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=(0, len(report_headers)))
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
