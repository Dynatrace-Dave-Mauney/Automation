# Post all segments matching the file path pattern to the specified environment.
# Uses a platform token!
# You can create these files by running the "download segments" python module

import codecs
import json
import glob

from Reuse import environment
from Reuse import new_platform_api


def run():
    pass
    post_segments('Sandbox', 'Assets/*.json')
    # post_segments('PreProd', 'Assets/*.json')
    # post_segments('Prod', 'Assets/*.json')
    # post_segments('Personal', 'Assets/*.json')


def post_segments(env_name, path):
    # print(f"post_segments({env_name}, {path})")
    friendly_function_name = 'Dynatrace Automation'
    _, env, client_id, client_secret = environment.get_client_environment_for_function(env_name, friendly_function_name)
    platform_token = environment.get_platform_token_for_function(env_name, friendly_function_name)

    scope = 'storage:filter-segments:read storage:filter-segments:write storage:filter-segments:share'

    # If Client Token is every required...
    # oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope=scope)
    oauth_bearer_token = platform_token
    for filename in glob.glob(path):
        print(filename)
        if filename.endswith(".json"):
            with codecs.open(filename, encoding='utf-8') as f:
                segment = f.read()
                formatted_segment = segment
                post_segment(env, oauth_bearer_token, formatted_segment)


def post_segment(env, oauth_bearer_token, payload):
    segment = json.loads(payload)
    segment_uid = segment.get('uid')
    segment_name = segment.get('name')
    optimistic_locking_version = segment.get('version')

    # segment['name'] = segment_name + '(PUT)'
    segment['isPublic'] = False
    payload = json.dumps(segment)

    print(f'Posting "{segment_name}" to {env}')
    api_url = f'{env}/platform/storage/filter-segments/v1/filter-segments'
    headers = {'accept': '*/*', 'Content-Type': 'application/json', 'Authorization': f'Bearer {str(oauth_bearer_token)}'}
    params = f'optimistic-locking-version={optimistic_locking_version}'
    print(payload, oauth_bearer_token)
    results = new_platform_api.post(oauth_bearer_token, api_url, payload)
    if results.status_code != 201:
        print(results.status_code, results.reason)
        exit(1)


if __name__ == '__main__':
    run()
