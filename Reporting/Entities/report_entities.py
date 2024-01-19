import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token, entity_types):

    entity_type_list = []
    if entity_types:
        entity_type_list = entity_types

    rows = []

    # Load the entity type list if not passed in
    if not entity_type_list:
        endpoint = '/api/v2/entityTypes'
        params = 'pageSize=500'
        entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

        for entities_json in entities_json_list:
            inner_entities_json_list = entities_json.get('types')
            for inner_entities_json in inner_entities_json_list:
                entity_type = inner_entities_json.get('type')
                entity_type_list.append(entity_type)

    for entity_type in entity_type_list:
        rows.extend(process_entity_type(env, token, entity_type))

    rows = sorted(rows)
    report_name = 'Entities'
    report_writer.initialize_text_file(None)
    report_headers = ('displayName', 'entityId')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def process_entity_type(env, token, entity_type):
    rows = []
    endpoint = '/api/v2/entities'
    entity_selector = f'&entitySelector=type({entity_type})'
    # fields = f'&fields="tags"'
    fields = ''
    raw_params = entity_selector + fields
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            # tags = inner_entities_json.get('tags')
            # rows.append((entity_id, display_name, str(tags)))
            rows.append((display_name, entity_id))

    return rows


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
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    # To process all entity types, pass "None"
    # process(env, token, None)

    # To process specific entity types, pass a list
    process(env, token, ['HOST', 'SERVICE', 'PROCESS_GROUP', 'APPLICATION', 'KUBERNETES_CLUSTER', 'KUBERNETES_NODE', 'KUBERNETES_SERVICE'])
    # process(env, token, ['HOST'])

    # entity_types_to_report = [
    #     'APPLICATION',
    #     'AUTO_SCALING_GROUP',
    #     'AWS_APPLICATION_LOAD_BALANCER',
    #     'AWS_AVAILABILITY_ZONE',
    #     'AWS_CREDENTIALS',
    #     'AWS_LAMBDA_FUNCTION',
    #     'AWS_NETWORK_LOAD_BALANCER',
    #     'CLOUD_APPLICATION',
    #     'CLOUD_APPLICATION_INSTANCE',
    #     'CLOUD_APPLICATION_NAMESPACE',
    #     'CONTAINER_GROUP',
    #     'CONTAINER_GROUP_INSTANCE',
    #     'CUSTOM_DEVICE',
    #     'CUSTOM_DEVICE_GROUP',
    #     'DISK',
    #     'DOCKER_CONTAINER_GROUP',
    #     'DOCKER_CONTAINER_GROUP_INSTANCE',
    #     'DYNAMO_DB_TABLE',
    #     'EBS_VOLUME',
    #     'EC2_INSTANCE',
    #     'ELASTIC_LOAD_BALANCER',
    #     'ENVIRONMENT',
    #     'GEOLOCATION',
    #     'GEOLOC_SITE',
    #     'HOST',
    #     'HOST_GROUP',
    #     'HTTP_CHECK',
    #     'HTTP_CHECK_STEP',
    #     'HYPERVISOR',
    #     'HYPERVISOR_CLUSTER',
    #     'HYPERVISOR_DISK',
    #     'KUBERNETES_CLUSTER',
    #     'KUBERNETES_NODE',
    #     'KUBERNETES_SERVICE',
    #     'NETWORK_INTERFACE',
    #     'OS',
    #     'PROCESS_GROUP',
    #     'PROCESS_GROUP_INSTANCE',
    #     'QUEUE',
    #     'QUEUE_INSTANCE',
    #     'RELATIONAL_DATABASE_SERVICE',
    #     'RUNTIME_COMPONENT',
    #     'S3BUCKET',
    #     'SERVICE',
    #     'SERVICE_INSTANCE',
    #     'SERVICE_METHOD',
    #     'SERVICE_METHOD_GROUP',
    #     'SYNTHETIC_LOCATION',
    #     'SYNTHETIC_TEST',
    #     'SYNTHETIC_TEST_STEP',
    #     'VCENTER',
    #     'VIRTUALMACHINE',
    #     'VMWARE_DATACENTER',
    # ]


if __name__ == '__main__':
    main()
