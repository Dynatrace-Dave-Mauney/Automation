"""

For safety, a clone will only be done for a specific synthetic.

Remove the if statement to clone all synthetics.

"""

import json

from Reuse import dynatrace_api
from Reuse import environment


def process(source_env, source_token, target_env, target_token):
    endpoint = '/api/v1/synthetic/monitors'
    params = ''
    monitors_json_list = dynatrace_api.get(source_env, source_token, endpoint, params)
    for monitors_json in monitors_json_list:
        inner_monitors_json_list = monitors_json.get('monitors')
        for inner_monitors_json in inner_monitors_json_list:
            entity_id = inner_monitors_json.get('entityId')
            monitor_name = inner_monitors_json.get('name')
            # if entity_id == 'HTTP_CHECK-59CB6082C98678C5':  # No Locations, for testing the location default
            if entity_id == 'SYNTHETIC_TEST-6ED223C2D0114F83':  # Has locations, is enabled, and works fine
                monitor = dynatrace_api.get_by_object_id(source_env, source_token, endpoint, entity_id)
                locations = monitor.get('locations')
                # Disable monitor to avoid runs until ready
                monitor['enabled'] = False
                # If no locations, use AWS N. Virgina to avoid a 404 on the POST
                if not locations:
                    monitor['locations'] = ['GEOLOCATION-9999453BE4BDB3CD']
                response = dynatrace_api.post(target_env, target_token, endpoint, json.dumps(monitor, indent=4, sort_keys=False))
                new_entity_id = json.loads(response.text).get('entityId')
                print(f'Cloned {monitor_name} ({entity_id}) from {source_env} to {target_env} with same name and new entity id of {new_entity_id}')


def main():
    source_env_name, source_env, source_token = environment.get_environment('Dev')
    target_env_name, target_env, target_token = environment.get_environment('Personal')
    process(source_env, source_token, target_env, target_token)


if __name__ == '__main__':
    main()
