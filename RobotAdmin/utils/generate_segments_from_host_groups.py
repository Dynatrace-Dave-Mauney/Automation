import copy
import json
import re
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import new_platform_api

configuration_object = environment.get_configuration_object('configurations.yaml')


def process(env, token, client_id, client_secret):
    return generate_segments(env, token, client_id, client_secret)


def generate_segments(env, token, client_id, client_secret):
    host_groups = []
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST_GROUP)'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            display_name = inner_entities_json.get('displayName')
            if display_name.startswith('a_') and display_name.endswith('_e_prod'):
                host_groups.append(display_name)

    host_groups = remove_duplicates(sorted(host_groups))

    for host_group in host_groups:
        result = post_segment(env, client_id, client_secret, host_group)
        print(result)


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


def post_segment(env, client_id, client_secret, host_group):
    segment_template = {
        "name": "{{.segment_name}}",
        "isPublic": True,
        "owner": "78cfc22b-0015-409e-bb07-0364eecc6ac3",
        "allowedOperations": [
            "READ"
        ],
        "includes": [
            {
                "filter": "{\"type\":\"Group\",\"range\":{\"from\":0,\"to\":{{.index1}}},\"logicalOperator\":\"AND\",\"explicit\":false,\"children\":[{\"type\":\"Statement\",\"range\":{\"from\":0,\"to\":{{.index2}}},\"key\":{\"type\":\"Key\",\"textValue\":\"dt.host_group.id\",\"value\":\"dt.host_group.id\",\"range\":{\"from\":0,\"to\":16}},\"operator\":{\"type\":\"ComparisonOperator\",\"textValue\":\"=\",\"value\":\"=\",\"range\":{\"from\":17,\"to\":18}},\"value\":{\"type\":\"String\",\"textValue\":\"{{.host_group1}}\",\"value\":\"{{.host_group2}}\",\"range\":{\"from\":19,\"to\":{{.index3}}}}}]}",
                "dataObject": "metrics",
                "applyTo": []
            }
        ],
        "version": 1
    }

    """
    "filter": "{\"type\":\"Group\",\"range\":{\"from\":0,\"to\":58},\"logicalOperator\":\"AND\",\"explicit\":false,\"children\":[{\"type\":\"Statement\",\"range\":{\"from\":0,\"to\":57},\"key\":{\"type\":\"Key\",\"textValue\":\"dt.host_group.id\",\"value\":\"dt.host_group.id\",\"range\":{\"from\":0,\"to\":16}},\"operator\":{\"type\":\"ComparisonOperator\",\"textValue\":\"=\",\"value\":\"=\",\"range\":{\"from\":17,\"to\":18}},\"value\":{\"type\":\"String\",\"textValue\":\"a_acquisitionmigration_f_apical_e_prod\",\"value\":\"a_acquisitionmigration_f_apical_e_prod\",\"range\":{\"from\":19,\"to\":57}}}]}",
    "filter": "{\"type\":\"Group\",\"range\":{\"from\":0,\"to\":{{.index1}}},\"logicalOperator\":\"AND\",\"explicit\":false,\"children\":[{\"type\":\"Statement\",\"range\":{\"from\":0,\"to\":{{.index2}}},\"key\":{\"type\":\"Key\",\"textValue\":\"dt.host_group.id\",\"value\":\"dt.host_group.id\",\"range\":{\"from\":0,\"to\":16}},\"operator\":{\"type\":\"ComparisonOperator\",\"textValue\":\"=\",\"value\":\"=\",\"range\":{\"from\":17,\"to\":18}},\"value\":{\"type\":\"String\",\"textValue\":\"{{.host_group1}}\",\"value\":\"{{.host_group2}}\",\"range\":{\"from\":19,\"to\":{{.index3}}}}}]}",
    """
    
    segment = copy.deepcopy(segment_template)
    # segment['name'] = segment_name
    # segment['rules'][0]['conditions'][0]['comparisonInfo']['value']['value'] = 'prod'
    # segment['rules'][0]['conditions'][1]['comparisonInfo']['value']['value'] = segment_name

    endpoint = '/platform/storage/filter-segments/v1/filter-segments'
    # dynatrace_api.post_object(f'{env}{endpoint}', token, json.dumps(segment))

    scope = 'storage:filter-segments:write storage:filter-segments:share'
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)

    host_group_index_short = str(len(host_group) + 19)
    host_group_index_long = str(len(host_group) + 20)

    # This leads to duplicate names...go with a one-to-one between host group and segement for now.
    # segment_name = re.sub('_f_.*', '', host_group)
    # segment_name = re.sub('_e_.*', '', segment_name)
    # segment_name = segment_name.replace('a_', '')

    segment_name = host_group[2:]
    segment_name = re.sub('_f_', ' ', segment_name)
    segment_name = re.sub('_e_prod', '', segment_name)
    segment_name = f'HG:{segment_name}'

    payload = json.dumps(segment)

    payload = payload.replace('{{.segment_name}}', segment_name)
    payload = payload.replace('{{.index1}}', host_group_index_long)
    payload = payload.replace('{{.index2}}', host_group_index_short)
    payload = payload.replace('{{.index3}}', host_group_index_short)
    payload = payload.replace('{{.host_group1}}', host_group)
    payload = payload.replace('{{.host_group2}}', host_group)

    # Convert classic env to new platform env
    env = env.replace('live', 'apps')
    
    results = new_platform_api.post(oauth_bearer_token, f'{env}{endpoint}', payload)
    return results.text


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    _, _, client_id, client_secret = environment.get_client_environment_for_function(env_name, friendly_function_name)
    process(env, token, client_id, client_secret)


if __name__ == '__main__':
    main()
