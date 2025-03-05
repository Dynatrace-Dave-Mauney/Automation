import json
import os
import shutil
import urllib.parse

from inspect import currentframe

from Reuse import dynatrace_api
from Reuse import environment

friendly_function_name = 'Dynatrace Automation Tools'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Prod'
# env_name_supplied = 'PreProd'
# env_name_supplied = 'Sandbox'
# env_name_supplied = 'Dev'
# env_name_supplied = 'Personal'
# env_name_supplied = 'Demo'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)


def list_settings20_objects():
    include_schemas = ['builtin:management-zones']

    endpoint = '/api/v2/settings/schemas'
    settings_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    schema_ids = []
    schema_dict = {}

    for settings_json in settings_json_list:
        inner_settings_json_list = settings_json.get('items')
        for inner_settings_json in inner_settings_json_list:
            schema_id = inner_settings_json.get('schemaId')
            schema_ids.append(schema_id)
            latest_schema_version = inner_settings_json.get('latestSchemaVersion')
            schema_dict[schema_id] = latest_schema_version

    for schema_id in sorted(schema_ids):
        if schema_id in include_schemas:
            endpoint = '/api/v2/settings/objects'
            raw_params = f'schemaIds={schema_id}&fields=objectId,value,scope&pageSize=500'
            params = urllib.parse.quote(raw_params, safe='/,&=')
            settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

            for settings_object in settings_object_list:
                items = settings_object.get('items')
                for item in items:
                    item_string = str(item)
                    if 'Full_Application' not in item_string  and 'ldap' not in item_string.lower() and 'jira' not in item_string.lower() and 'confluence' not in item_string.lower():
                        object_id = item.get('objectId')
                        print('DELETING:', object_id)
                        dynatrace_api.delete_object(f'{env}{endpoint}/{object_id}', token)


if __name__ == '__main__':
    list_settings20_objects()
