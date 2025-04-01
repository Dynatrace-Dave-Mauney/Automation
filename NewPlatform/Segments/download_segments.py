import json
import os
import re
import urllib.parse

from Reuse import environment
from Reuse import new_platform_api

# Populated from configuration file
owner_id_list = None


def process(env, env_name, client_id, client_secret):
    configuration_file = 'configurations.yaml'
    my_owner_ids = environment.get_configuration('my_owner_ids', configuration_file=configuration_file)

    if my_owner_ids:
        print('Downloading segment owned by:', my_owner_ids)

    scope = 'storage:filter-segments:read'

    output_directory = environment.get_output_directory_name(f"Downloads/{env_name}")
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/storage/filter-segments/v1/filter-segments', params=params)
    segments_json = json.loads(results.text)
    segment_list = segments_json.get('filterSegments')
    for segment in segment_list:
        print(segment)
        segment_uid = segment.get('uid')
        segment_name = segment.get('name')
        segment_owner = segment.get('owner')
        # segment_is_public = segment.get('isPublic')
        # segment_version = segment.get('version')

        # if my_owner_ids and segment_owner in my_owner_ids:
        if not my_owner_ids or (my_owner_ids and segment_owner in my_owner_ids):
            pass
        else:
            continue

        raw_params = 'add-fields=INCLUDES&add-fields=VARIABLES&add-fields=EXTERNALID&add-fields=RESOURCECONTEXT'
        params = urllib.parse.quote(raw_params, safe='/,&=')

        segment_results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/storage/filter-segments/v1/filter-segments/{segment_uid}', params)
        segment_json = json.loads(segment_results.text)
        clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{segment_name}.json')
        segment_file_name = os.path.join(output_directory, clean_filename)
        formatted_segment = json.dumps(segment_json, indent=4, sort_keys=False)
        print(f'Writing file {segment_file_name}')
        with open(segment_file_name, 'w', encoding='utf8') as output_file:
            output_file.write('%s' % formatted_segment)


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Sandbox'
    #
    # env_name_supplied = 'Upper'
    # env_name_supplied = 'Lower'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, env_name, client_id, client_secret)


if __name__ == '__main__':
    main()
