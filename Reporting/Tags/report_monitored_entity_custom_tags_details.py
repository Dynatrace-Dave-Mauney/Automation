# Report manual tags on a specified monitored entity

import dynatrace_rest_api_helper
import os
import urllib.parse


def process(env, token, print_mode):
    endpoint = '/api/v2/tags'
    entity_name = 'SYNTHETIC_TEST-64750847343FE4CD'
    entity_name = 'HTTP_CHECK-F5074A0CB1B0B506'
    print('Tags for ' + entity_name)
    raw_params = f'entitySelector=entityId(HTTP_CHECK-DD6BA68782BF144B)'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    manual_tags_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)
    print('key' + '|' + 'value' + '|' + 'stringRepresentation')

    for manual_tags_json in manual_tags_json_list:
        inner_manual_tags_json_list = manual_tags_json.get('tags')
        for inner_manual_tags_json in inner_manual_tags_json_list:
            key = inner_manual_tags_json.get('key', '')
            value = inner_manual_tags_json.get('value', '')
            string_representation = inner_manual_tags_json.get('stringRepresentation', '')
            print(key + '|' + value + '|' + string_representation)


def main():
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, True)


if __name__ == '__main__':
    main()
