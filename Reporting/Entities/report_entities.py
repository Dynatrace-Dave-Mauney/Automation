import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []
    entity_type_list = []

    endpoint = '/api/v2/entityTypes'
    params = ''
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('types')
        for inner_entities_json in inner_entities_json_list:
            entity_type = inner_entities_json.get('type')
            entity_type_list.append(entity_type)

    for entity_type in entity_type_list:
        rows.extend(process_entity_type(env, token, entity_type))

    report_name = 'Entities'
    report_writer.initialize_text_file(None)
    report_headers = ('entityId', 'displayName')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def process_entity_type(env, token, entity_type):
    rows = []
    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector)
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            rows.append((entity_id, display_name))

    return rows


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    
    process(env, token)

    # More selective techniques
    # process_entity_type(env, token, 'PROCESS_GROUP')
    # process_entity_type(env, token, 'SERVICE')
    # process_entity_type(env, token, 'HOST')

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
    #
    # for entity_type in entity_types_to_report:
    #     process_entity_type(env, token, entity_type)


if __name__ == '__main__':
    main()
