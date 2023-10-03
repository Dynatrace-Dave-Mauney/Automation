"""

For safety, a repair will only be done for synthetics with very specific criteria.

Change the logic to suit your use case.

"""

import json

from Reuse import dynatrace_api
from Reuse import environment


def process(target_env, target_token):
    endpoint = '/api/v1/synthetic/monitors'
    params = ''
    monitors_json_list = dynatrace_api.get(target_env, target_token, endpoint, params)
    for monitors_json in monitors_json_list:
        inner_monitors_json_list = monitors_json.get('monitors')
        for inner_monitors_json in inner_monitors_json_list:
            monitor_type = inner_monitors_json.get('type')
            if monitor_type == 'HTTP':
                entity_id = inner_monitors_json.get('entityId')
                monitor_name = inner_monitors_json.get('name')
                monitor = dynatrace_api.get_by_object_id(target_env, target_token, endpoint, entity_id)
                first_step_description = monitor.get('script').get('requests')[0].get('description')
                if first_step_description == 'HTTP Check Synthetic created by automation script':
                    first_step_url = monitor.get('script').get('requests')[0].get('url')
                    new_first_step_description = first_step_url.strip().lower().replace('https://', '')
                    print(monitor_name, first_step_description, first_step_url, new_first_step_description)
                    monitor['script']['requests'][0]['description'] = new_first_step_description
                    response = dynatrace_api.put(target_env, target_token, endpoint, entity_id, json.dumps(monitor, indent=4, sort_keys=False))
                    print(f'Repaired {monitor_name} ({entity_id}) in {target_env}: {new_first_step_description}')


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
