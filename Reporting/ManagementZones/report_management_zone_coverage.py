import copy
import os
import requests
import urllib.parse
import xlsxwriter

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
    mz_coverage_dict = {}

    counts_by_entity_type_template = {}
    for entity_type_of_interest in entity_types_of_interest:
        counts_by_entity_type_template[entity_type_of_interest] = 0

    endpoint = '/api/config/v1/managementZones'
    params = ''
    management_zone_json_list = get_rest_api_json(env, token, endpoint, params)

    for management_zone_json in management_zone_json_list:
        inner_management_zone_json_list = management_zone_json.get('values')
        for inner_management_zone_json in inner_management_zone_json_list:
            # mz_id = inner_management_zone_json.get('id')
            mz_name = inner_management_zone_json.get('name')
            # print(mz_name)
            mz_coverage_dict[mz_name] = copy.deepcopy(counts_by_entity_type_template)

    # print(mz_coverage_dict)

    for entity_type_of_interest in entity_types_of_interest:
        get_mz_coverage_for_entity_type(env, token, entity_type_of_interest, mz_coverage_dict)

    write_xlsx(env_name, mz_coverage_dict)


def write_xlsx(env_name, mz_coverage_dict):
    workbook = xlsxwriter.Workbook(f'../../$Output/Reporting/ManagementZones/Management_Zone_Coverage_{env_name}.xlsx')
    worksheet = workbook.add_worksheet()

    row_index = 0
    column_index = 0

    headers = ['Management Zone']
    headers.extend(entity_types_of_interest)

    for header in headers:
        worksheet.write(row_index, column_index, header)
        column_index += 1

    row_index += 1

    column_index = 0
    for key in sorted(mz_coverage_dict.keys()):
        worksheet.write(row_index, column_index, key)
        column_index += 1

        for entity_type in entity_types_of_interest:
            worksheet.write(row_index, column_index, mz_coverage_dict.get(key).get(entity_type))
            column_index += 1
        column_index = 0
        row_index += 1

    workbook.close()


def get_mz_coverage_for_entity_type(env, token, entity_type, mz_coverage_dict):
    # Skip special entity types used for counting only
    if entity_type == 'DATABASE_SERVICE':
        return

    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    raw_params = f'&entitySelector={entity_selector}&fields=managementZones'
    if entity_type == 'SERVICE':
        raw_params += ',properties.serviceType'
    # raw_params = f'&entitySelector={entity_selector}'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = get_rest_api_json(env, token, endpoint, params)
    # print(entities_json_list)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            # print(inner_entities_json)
            # entity_id = inner_entities_json.get('entityId')
            # entity_type = inner_entities_json.get('type')
            # display_name = inner_entities_json.get('displayName')
            management_zone_list = inner_entities_json.get('managementZones')
            # print(entity_id + '|' + display_name + '|' + str(management_zone_list))

            if management_zone_list:
                increment_mz_coverage_dict_counts(entity_type, management_zone_list, mz_coverage_dict)
                if entity_type == 'SERVICE' and inner_entities_json.get('properties').get('serviceType') == 'DATABASE_SERVICE':
                    increment_mz_coverage_dict_counts('DATABASE_SERVICE', management_zone_list, mz_coverage_dict)

    # print(mz_coverage_dict)


def increment_mz_coverage_dict_counts(entity_type, management_zone_list, mz_coverage_dict):
    for management_zone in management_zone_list:
        mz_name = management_zone.get('name')
        mz_coverage_dict[mz_name][entity_type] += 1


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

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


def main():
    # print('Management Zone Coverage')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')
    # tenant = os.environ.get(tenant_key)
    # token = os.environ.get(token_key)
    # env = f'https://{tenant}.live.dynatrace.com'
    # process(env_name, env, token)

    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'
    process(env_name, env, token)

    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # tenant = os.environ.get(tenant_key)
    # token = os.environ.get(token_key)
    # env = f'https://{tenant}.live.dynatrace.com'
    # process(env, token)
    #
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # tenant = os.environ.get(tenant_key)
    # token = os.environ.get(token_key)
    # env = f'https://{tenant}.live.dynatrace.com'
    # process(env, token)
    #


if __name__ == '__main__':
    main()
