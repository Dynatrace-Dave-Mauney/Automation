"""

For safety, a clone will only be done for a specific synthetic.

Remove the if statement to clone all synthetics.

"""

import json
import os

from Reuse import dynatrace_api
from Reuse import environment


def process():
    source_env_name, source_env, source_token = environment.get_environment('Upper')
    target_env_name, target_env, target_token = environment.get_environment('Upper')

    # Could be made more efficient by looping thru the clone_synthetics_dictionary keys, but that would
    # eliminate the "clone all synthetics" use case, so leaving it inefficient
    configuration_path = 'configurations.yaml'
    if os.path.isfile(configuration_path):
        locations_dictionary = environment.get_configuration('locations', configuration_file=configuration_path)
        locations = locations_dictionary.get(target_env_name)
        clone_synthetics_dictionary = environment.get_configuration('clone_synthetics_dictionary', configuration_file=configuration_path)
        clone_synthetics_dictionary_by_target_environment = clone_synthetics_dictionary.get(target_env_name)
        print('target_env_name:', target_env_name)
        print('locations_dictionary:', locations_dictionary)
        print('locations:', locations)
        print('clone_synthetics_dictionary:', clone_synthetics_dictionary)
        print('clone_synthetics_dictionary_by_target_environment:', clone_synthetics_dictionary_by_target_environment)

    endpoint = '/api/v1/synthetic/monitors'
    monitors_json_list = dynatrace_api.get_json_list_with_pagination(f'{source_env}{endpoint}', source_token)
    for monitors_json in monitors_json_list:
        inner_monitors_json_list = monitors_json.get('monitors')
        for inner_monitors_json in inner_monitors_json_list:
            entity_id = inner_monitors_json.get('entityId')
            # if entity_id == 'HTTP_CHECK-59CB6082C98678C5':  # No Locations, for testing the location default
            # if entity_id == 'SYNTHETIC_TEST-6ED223C2D0114F83':  # Has locations, is enabled, and works fine

            # target_clone_list = ['HTTP_CHECK-D0861DC85767C267',  # Borrower App
            #                      'HTTP_CHECK-4DB0B6D1E3D4F111',  # Curity
            #                      'HTTP_CHECK-9D279BA0EC309D58',  # Pipeline
            #                      'HTTP_CHECK-18CE5DF4364A7A0E'   # Get Current Offer
            #                      ]
            # if entity_id in target_clone_list:

            if entity_id in clone_synthetics_dictionary_by_target_environment:
                r = dynatrace_api.get_without_pagination(f'{source_env}{endpoint}/{entity_id}', source_token)
                monitor = r.json()
                # Disable monitor to avoid runs until ready
                monitor['enabled'] = False

                monitor_name = inner_monitors_json.get('name')
                if target_env_name == 'Lower':
                    monitor_name = monitor_name.replace('PROD', 'INT')
                if target_env_name == 'Upper':
                    monitor_name = monitor_name.replace('PROD', 'STAGE')

                monitor['name'] = monitor_name
                monitor.pop('managementZones')
                # monitor['locations'] = ['SYNTHETIC_LOCATION-42938461CD823624']  # Lower S01 Datacenter
                monitor['locations'] = locations

                print(f'Attempting a clone of "{monitor_name}"')

                new_values_dictionary = clone_synthetics_dictionary_by_target_environment[entity_id]
                short_name = new_values_dictionary['short_name']
                new_domain = new_values_dictionary['domain']
                new_applications = new_values_dictionary['application_id_list']
                new_description = new_values_dictionary['description']
                new_url = new_values_dictionary['url']
                new_credentials_vault_id = new_values_dictionary['credentials_vault_id']

                # print(new_values_dictionary)
                # print(short_name)
                # print(new_domain)
                # print(new_applications)
                # print(new_description)
                # print(new_url)
                # print(new_credentials_vault_id)

                monitor['script']['requests'][0]['description'] = new_description
                monitor['script']['requests'][0]['url'] = new_url
                monitor['manuallyAssignedApps'] = new_applications
                monitor['requests'][0]['name'] = new_description
                if new_credentials_vault_id:
                    monitor['script']['requests'][0]['authentication']['credentials'] = new_credentials_vault_id

                response = dynatrace_api.post_object(f'{target_env}{endpoint}', target_token, json.dumps(monitor, indent=4, sort_keys=False))
                new_entity_id = json.loads(response.text).get('entityId')
                print(f'Cloned {monitor_name} ({entity_id}) from {source_env} to {target_env} with entity id of {new_entity_id}')

                # print(f'Would have cloned "{monitor_name}" from {source_env} to {target_env}')


def main():
    process()


if __name__ == '__main__':
    main()
