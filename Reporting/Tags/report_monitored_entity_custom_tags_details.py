# Report manual tags on a specified monitored entity

import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token, print_mode):
    endpoint = '/api/v2/tags'
    entity_name = 'SYNTHETIC_TEST-64750847343FE4CD'
    entity_name = 'HTTP_CHECK-F5074A0CB1B0B506'
    print('Tags for ' + entity_name)
    raw_params = f'entitySelector=entityId(HTTP_CHECK-DD6BA68782BF144B)'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    manual_tags_json_list = dynatrace_api.get(env, token, endpoint, params)
    print('key' + '|' + 'value' + '|' + 'stringRepresentation')

    for manual_tags_json in manual_tags_json_list:
        inner_manual_tags_json_list = manual_tags_json.get('tags')
        for inner_manual_tags_json in inner_manual_tags_json_list:
            key = inner_manual_tags_json.get('key', '')
            value = inner_manual_tags_json.get('value', '')
            string_representation = inner_manual_tags_json.get('stringRepresentation', '')
            print(key + '|' + value + '|' + string_representation)


def main():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
