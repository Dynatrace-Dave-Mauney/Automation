import copy
import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

configuration_object = environment.get_configuration_object('configurations.yaml')


def process(env, token):
    return generate_management_zones(env, token)


def generate_management_zones(env, token):
    management_zones = []
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST_GROUP)'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            display_name = inner_entities_json.get('displayName')
            management_zones.append(display_name)

    management_zones = remove_duplicates(sorted(management_zones))

    for management_zone in management_zones:
        post_management_zone(env, token, management_zone)

def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


def post_management_zone(env, token, management_zone_name):
    management_zone_template = {
    "metadata": {
        "currentConfigurationVersions": [
            "1.0.13"
        ],
        "configurationVersions": [],
        "clusterVersion": "1.330.55.20260126-105640"
    },
    "name": "HG: $$HG$$",
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
                        "attribute": "HOST_GROUP_NAME",
                        "type": "STATIC"
                    },
                    "comparisonInfo": {
                        "type": "STRING",
                        "operator": "EQUALS",
                        "value": "$$HG$$",
                        "negate": False,
                        "caseSensitive": True
                    }
                }
            ]
        }
    ],
    "dimensionalRules": [],
    "entitySelectorBasedRules": []
}
    management_zone = copy.deepcopy(management_zone_template)
    management_zone['name'] = f'HG: {management_zone_name}'
    management_zone['rules'][0]['conditions'][0]['comparisonInfo']['value'] = management_zone_name

    endpoint = '/api/config/v1/managementZones'
    r = dynatrace_api.post_object(f'{env}{endpoint}', token, json.dumps(management_zone), handle_exceptions=False, exit_on_exception=False)
    if r.status_code != 400:
        print(f"Added management zone: {management_zone['name']}")


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
