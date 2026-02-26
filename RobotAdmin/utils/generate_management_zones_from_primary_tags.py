import copy
import json
import re
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

update_mode = True


def process(env, token):
    return generate_management_zones(env, token)


def generate_management_zones(env, token):
    existing_management_zones = []

    if update_mode:
        existing_management_zones = get_management_zones(env, token)

    management_zones = []
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            tags = inner_entities_json.get('tags')

            for tag in tags:
                tag_key = tag.get('key')
                if tag_key.startswith('primary_tags.'):
                    tag_name = tag_key.replace('primary_tags.', '')
                    tag_value = tag.get('value')
                    mz_tag = f'{tag_name}={tag_value}'
                    if mz_tag not in management_zones:
                        management_zones.append(mz_tag)

    for management_zone in management_zones:
        tokens = management_zone.split('=')
        mz_prefix = tokens[0].upper()
        value = tokens[1]
        management_zone_formatted = f'{mz_prefix}:{value}'

        if update_mode:
            if management_zone_formatted not in existing_management_zones:
                print('Posting management zone:', management_zone_formatted)
                post_management_zone(env, token, management_zone)
            else:
                print('Skipping exiting management zone:', management_zone_formatted)
        else:
            print('Posting management zone:', management_zone_formatted)
            post_management_zone(env, token, management_zone)

def post_management_zone(env, token, management_zone_name):
    management_zone_template = {
    "metadata": {
        "currentConfigurationVersions": [
            "1.0.13"
        ],
        "configurationVersions": [],
        "clusterVersion": "1.330.55.20260126-105640"
    },
    "name": "$$NAME$$",
    "description": None,
    "rules": [
        {
            "type": "PROCESS_GROUP",
            "enabled": True,
            "propagationTypes": [
                "PROCESS_GROUP_TO_HOST",
                "PROCESS_GROUP_TO_SERVICE"
            ],
            "conditions": [
                {
                    "key": {
                        "attribute": "HOST_TAGS",
                        "type": "STATIC"
                    },
                    "comparisonInfo": {
                        "type": "TAG",
                        "operator": "EQUALS",
                        "value": {
                            "context": "ENVIRONMENT",
                            "key": "$$TAG_KEY$$",
                            "value": "$$TAG_VALUE$$"
                        },
                        "negate": False
                    }
                }
            ]
        }
    ],
    "dimensionalRules": [],
    "entitySelectorBasedRules": []
}
    management_zone = copy.deepcopy(management_zone_template)

    tokens = management_zone_name.split('=')
    key = f'primary_tags.{tokens[0]}'
    value = tokens[1]
    mz_prefix = tokens[0].upper()

    management_zone['name'] = f'{mz_prefix}:{value}'
    # print(management_zone['name'])
    management_zone['rules'][0]['conditions'][0]['comparisonInfo']['value']['key'] = key
    management_zone['rules'][0]['conditions'][0]['comparisonInfo']['value']['value'] = value

    endpoint = '/api/config/v1/managementZones'
    r = dynatrace_api.post_object(f'{env}{endpoint}', token, json.dumps(management_zone), handle_exceptions=False, exit_on_exception=False)
    if r.status_code != 400:
        print(f"Added management zone: {management_zone['name']}")

def get_management_zones(env,token):
    management_zones = []
    endpoint = '/api/config/v1/managementZones'
    management_zones_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    mz_list = management_zones_json_list[0].get('values')
    for mz in mz_list:
        management_zones.append(mz.get('name'))

    return management_zones


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
