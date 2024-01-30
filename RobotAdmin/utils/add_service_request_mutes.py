import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def process():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    env_name_supplied = 'Personal'  # For Safety
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    tenable_request_already_muted_service_list = []
    tenable_request_needs_muted_service_list = []

    item_list = []
    endpoint = '/api/v2/settings/objects'
    raw_params = 'schemaIds=builtin:settings.mutedrequests&fields=objectId,value,scope&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    json_response_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for json_response in json_response_list:
        item_list.extend(json_response.get('items'))

    # print(item_list)

    for item in item_list:
        # print(item)
        # object_id = item.get('objectId')
        # print('object_id: ' + object_id)
        # value = item.get('value')
        scope = item.get('scope')
        # print('value: ' + str(value))
        # print('scope: ' + scope)

        muted_request_list = item.get('value').get('mutedRequestNames', [])
        if 'Tenable Request' in muted_request_list:
            tenable_request_already_muted_service_list.append(scope)

    # print('tenable_request_already_muted_service_list size: ' + str(len(tenable_request_already_muted_service_list)))
    # print('tenable_request_already_muted_service_list: ' + str(tenable_request_already_muted_service_list))

    endpoint = '/api/v2/entities'
    raw_params = 'entitySelector=type(SERVICE)&fields=properties.SERVICE_TYPE&from=now-1y&pageSize=4000'
    params = urllib.parse.quote(raw_params, safe='/,&=?')

    service_list = []
    json_response_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    for json_response in json_response_list:
        service_list.extend(json_response.get('entities'))

    for service in service_list:
        service_id = service.get('entityId')
        service_type = service.get('properties').get('serviceType')
        # print(service)
        if service_type == 'WEB_REQUEST_SERVICE' or service_type == 'WEB_SERVICE':
            if service_id not in tenable_request_already_muted_service_list:
                service_display_name = service.get('displayName')
                if not service_display_name.startswith('Requests to'):
                    # print(service_id + ':' + service_display_name)
                    tenable_request_needs_muted_service_list.append(service_id)

    # print(tenable_request_needs_muted_service_list)

    payload_list = []
    for tenable_request_needs_muted_service in tenable_request_needs_muted_service_list:
        # print(tenable_request_needs_muted_service)
        endpoint = '/api/v2/settings/objects'
        payload_list.append({"schemaId": "builtin:settings.mutedrequests", "scope": tenable_request_needs_muted_service, "value": {"mutedRequestNames": ["Tenable Request"]}})

    payload_list_size = len(payload_list)
    if payload_list_size > 0:
        # The API call cannot handle too many requests in a single list, so...
        # partition the list using list comprehension
        partition_size = 1000
        partitioned_payload_list = [payload_list[i:i + partition_size] for i in range(0, len(payload_list), partition_size)]
        # print(partitioned_payload_list)
        for partition in partitioned_payload_list:
            # print(partition)
            dynatrace_api.post_object(f'{env}{endpoint}', token, json.dumps(partition))
    else:
        print('No services need mute added at this time')


if __name__ == '__main__':
    process()
