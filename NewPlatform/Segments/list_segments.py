import json

from Reuse import environment
from Reuse import new_platform_api
from Reuse import report_writer


def process(env, client_id, client_secret):
    scope = 'storage:filter-segments:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/storage/filter-segments/v1/filter-segments', params)
    segments_json = json.loads(results.text)
    print(segments_json)
    segment_list = segments_json.get('filterSegments')
    headers = [['UID', 'Name', 'isPublic', 'Owner', 'Version']]
    rows = []
    for segment in segment_list:
        segment_uid = segment.get('uid')
        segment_name = segment.get('name')
        segment_is_public = segment.get('isPublic')
        segment_owner = segment.get('owner')
        segment_version = segment.get('version')
        rows.append([segment_uid, segment_name, segment_is_public, segment_owner, segment_version])

    report_writer.print_rows(headers, sorted(rows))


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
    process(env, client_id, client_secret)


if __name__ == '__main__':
    main()
