import copy
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

# Typical AWS customer list.
# Amend as needed from 'monitored_entity_filters', which was obtained by running 'dump_monitored_entity_filters()'
# in 'Tools/APISpecs/dump_config_v1_spec_details_of_interest.py'
# NOTE: DATABASE_SERVICE is "made up" to capture coverage of databases specifically.
# NOTE: Some entities below are commented out only because they are not used at my current customer.
entity_types_of_interest = [
    'APPLICATION',
    'AUTO_SCALING_GROUP',
    'AWS_APPLICATION_LOAD_BALANCER',
    'AWS_AVAILABILITY_ZONE',
    'AWS_CREDENTIALS',
    'AWS_LAMBDA_FUNCTION',
    'AWS_NETWORK_LOAD_BALANCER',
    'CLOUD_APPLICATION',
    'CLOUD_APPLICATION_INSTANCE',
    'CLOUD_APPLICATION_NAMESPACE',
    'CONTAINER_GROUP',
    # 'CUSTOM_APPLICATION',
    'CUSTOM_DEVICE',
    'DATABASE_SERVICE',
    # 'DOCKER_CONTAINER_GROUP',
    # 'DYNAMO_DB_TABLE',
    # 'EBS_VOLUME',
    'EC2_INSTANCE',
    # 'ELASTIC_LOAD_BALANCER',
    'HOST',
    'HTTP_CHECK',
    'HYPERVISOR',
    'KUBERNETES_CLUSTER',
    'KUBERNETES_NODE',
    # 'KUBERNETES_SERVICE',
    # 'MOBILE_APPLICATION',
    'PROCESS_GROUP',
    # 'QUEUE',
    'RELATIONAL_DATABASE_SERVICE',
    'SERVICE',
    'SYNTHETIC_TEST',
    # 'VIRTUALMACHINE',
    # 'VMWARE_DATACENTER',
]

entity_types_of_interest_short_list = [
    'APPLICATION',
    'AWS_CREDENTIALS',
    'HOST',
    'HTTP_CHECK',
    'KUBERNETES_CLUSTER',
    'PROCESS_GROUP',
    'SERVICE',
    'SYNTHETIC_TEST',
]

# These are close to being the full list of possible mz entities
monitored_entity_filters = [
    'APM_SECURITY_GATEWAY',
    'APPLICATION',
    'APPLICATION_METHOD',
    'APPLICATION_METHOD_GROUP',
    'APPMON_SERVER',
    'APPMON_SYSTEM_PROFILE',
    'AUTO_SCALING_GROUP',
    # 'AUXILIARY_SYNTHETIC_TEST',
    'AWS_APPLICATION_LOAD_BALANCER',
    'AWS_AVAILABILITY_ZONE',
    'AWS_CREDENTIALS',
    'AWS_LAMBDA_FUNCTION',
    'AWS_NETWORK_LOAD_BALANCER',
    'AZURE_API_MANAGEMENT_SERVICE',
    'AZURE_APPLICATION_GATEWAY',
    'AZURE_COSMOS_DB',
    'AZURE_CREDENTIALS',
    'AZURE_EVENT_HUB',
    'AZURE_EVENT_HUB_NAMESPACE',
    'AZURE_FUNCTION_APP',
    'AZURE_IOT_HUB',
    'AZURE_LOAD_BALANCER',
    'AZURE_MGMT_GROUP',
    'AZURE_REDIS_CACHE',
    'AZURE_REGION',
    'AZURE_SERVICE_BUS_NAMESPACE',
    'AZURE_SERVICE_BUS_QUEUE',
    'AZURE_SERVICE_BUS_TOPIC',
    'AZURE_SQL_DATABASE',
    'AZURE_SQL_ELASTIC_POOL',
    'AZURE_SQL_SERVER',
    'AZURE_STORAGE_ACCOUNT',
    'AZURE_SUBSCRIPTION',
    'AZURE_TENANT',
    'AZURE_VM',
    'AZURE_VM_SCALE_SET',
    'AZURE_WEB_APP',
    # 'CF_APPLICATION',
    # 'CF_FOUNDATION',
    'CINDER_VOLUME',
    'CLOUD_APPLICATION',
    'CLOUD_APPLICATION_INSTANCE',
    'CLOUD_APPLICATION_NAMESPACE',
    # 'CLOUD_NETWORK_INGRESS',
    # 'CLOUD_NETWORK_POLICY',
    'CONTAINER_GROUP',
    'CONTAINER_GROUP_INSTANCE',
    'CUSTOM_APPLICATION',
    'CUSTOM_DEVICE',
    'CUSTOM_DEVICE_GROUP',
    'DCRUM_APPLICATION',
    'DCRUM_SERVICE',
    'DCRUM_SERVICE_INSTANCE',
    'DEVICE_APPLICATION_METHOD',
    'DISK',
    'DOCKER_CONTAINER_GROUP',
    'DOCKER_CONTAINER_GROUP_INSTANCE',
    'DYNAMO_DB_TABLE',
    'EBS_VOLUME',
    'EC2_INSTANCE',
    'ELASTIC_LOAD_BALANCER',
    'ENVIRONMENT',
    'EXTERNAL_SYNTHETIC_TEST_STEP',
    'GCP_ZONE',
    'GEOLOCATION',
    'GEOLOC_SITE',
    'GOOGLE_COMPUTE_ENGINE',
    'HOST',
    'HOST_GROUP',
    'HTTP_CHECK',
    'HTTP_CHECK_STEP',
    'HYPERVISOR',
    'KUBERNETES_CLUSTER',
    'KUBERNETES_NODE',
    'KUBERNETES_SERVICE',
    'MOBILE_APPLICATION',
    'NETWORK_INTERFACE',
    'NEUTRON_SUBNET',
    'OPENSTACK_PROJECT',
    'OPENSTACK_REGION',
    'OPENSTACK_VM',
    'OS',
    'PROCESS_GROUP',
    'PROCESS_GROUP_INSTANCE',
    'QUEUE',
    'RELATIONAL_DATABASE_SERVICE',
    'SERVICE',
    'SERVICE_INSTANCE',
    'SERVICE_METHOD',
    'SERVICE_METHOD_GROUP',
    'SWIFT_CONTAINER',
    'SYNTHETIC_LOCATION',
    'SYNTHETIC_TEST',
    'SYNTHETIC_TEST_STEP',
    'VIRTUALMACHINE',
    'VMWARE_DATACENTER',
]


def process(env_name, env, token):
    file_name = f'../../$Output/Reporting/ManagementZones/Management_Zone_Coverage_{env_name}.xlsx'

    mz_coverage_dict = {}

    counts_by_entity_type_template = {}
    for entity_type_of_interest in entity_types_of_interest:
        counts_by_entity_type_template[entity_type_of_interest] = 0

    endpoint = '/api/config/v1/managementZones'
    params = ''
    management_zone_json_list = dynatrace_api.get(env, token, endpoint, params)

    for management_zone_json in management_zone_json_list:
        inner_management_zone_json_list = management_zone_json.get('values')
        for inner_management_zone_json in inner_management_zone_json_list:
            mz_name = inner_management_zone_json.get('name')
            mz_coverage_dict[mz_name] = copy.deepcopy(counts_by_entity_type_template)

    for entity_type_of_interest in entity_types_of_interest:
        get_mz_coverage_for_entity_type(env, token, entity_type_of_interest, mz_coverage_dict)

    rows = []
    for key in sorted(mz_coverage_dict.keys()):
        row = [key]
        for entity_type in entity_types_of_interest:
            row.append(mz_coverage_dict.get(key).get(entity_type))
        rows.append(row)

    # write_xlsx(env_name, mz_coverage_dict)
    write_console(rows)
    write_xlsx(file_name, rows)


def write_console(rows):
    title = 'Management Zone Coverage'
    headers = ['Management Zone']
    headers.extend(entity_types_of_interest)
    delimiter = '|'
    report_writer.write_console(title, headers, rows, delimiter)


def write_xlsx(xlsx_file_name, rows):
    worksheet_name = 'Management Zone Coverage'
    headers = ['Management Zone']
    headers.extend(entity_types_of_interest)
    header_format = None
    auto_filter = (0, len(headers))
    report_writer.write_xlsx(xlsx_file_name, worksheet_name, headers, rows, header_format, auto_filter)
    print(f'Output written to {xlsx_file_name}')


def get_mz_coverage_for_entity_type(env, token, entity_type, mz_coverage_dict):
    # Skip special entity types used for counting only
    if entity_type == 'DATABASE_SERVICE':
        return

    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    raw_params = f'&entitySelector={entity_selector}&fields=managementZones'
    if entity_type == 'SERVICE':
        raw_params += ',properties.serviceType'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            management_zone_list = inner_entities_json.get('managementZones')
            if management_zone_list:
                increment_mz_coverage_dict_counts(entity_type, management_zone_list, mz_coverage_dict)
                if entity_type == 'SERVICE' and inner_entities_json.get('properties').get('serviceType') == 'DATABASE_SERVICE':
                    increment_mz_coverage_dict_counts('DATABASE_SERVICE', management_zone_list, mz_coverage_dict)


def increment_mz_coverage_dict_counts(entity_type, management_zone_list, mz_coverage_dict):
    for management_zone in management_zone_list:
        mz_name = management_zone.get('name')
        mz_coverage_dict[mz_name][entity_type] += 1


def main():
    # env_name, env, token = environment.get_environment('Prod')
    # process(env_name, env, token)

    # env_name, env, token = environment.get_environment('Prep')
    # process(env_name, env, token)

    # env_name, env, token = environment.get_environment('Dev')
    # process(env_name, env, token)

    env_name, env, token = environment.get_environment('Personal')
    process(env_name, env, token)

    # env_name, env, token = environment.get_environment('FreeTrial1')
    # process(env_name, env, token)


if __name__ == '__main__':
    main()
