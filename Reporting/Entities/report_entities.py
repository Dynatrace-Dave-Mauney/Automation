import os
import requests
import urllib.parse


def report_all_entity_types(env, token):
    entity_type_list = []

    endpoint = '/api/v2/entityTypes'
    params = ''
    entities_json_list = get_rest_api_json(env, token, endpoint, params)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('types')
        for inner_entities_json in inner_entities_json_list:
            entity_type = inner_entities_json.get('type')
            entity_type_list.append(entity_type)

    for entity_type in entity_type_list:
        report_entity_type(env, token, entity_type)


def report_entity_type(env, token, entity_type):
    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector)
    entities_json_list = get_rest_api_json(env, token, endpoint, params)
    # print(entities_json_list)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            # print(inner_entities_json)
            entity_id = inner_entities_json.get('entityId')
            # entity_type = inner_entities_json.get('type')
            display_name = inner_entities_json.get('displayName')
            print(entity_id + '|' + display_name)


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    json_data = resp.json()

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json_data) is list:
        # DEBUG:
        # print(json_data)
        return json_data

    json_list = [json_data]
    next_page_key = json_data.get('nextPageKey')

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

        json_data = resp.json()
        # print(json_data)

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def main():
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    print('entityId' + '|' + 'displayName')

    report_all_entity_types(env, token)
    exit()

    # More selective techniques

    # report_entity_type(env, token, 'PROCESS_GROUP')
    # report_entity_type(env, token, 'SERVICE')
    # report_entity_type(env, token, 'HOST')

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
    #     report_entity_type(env, token, entity_type)


if __name__ == '__main__':
    main()
