import copy
import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

friendly_function_name = 'Dynatrace Automation'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Prod'
# env_name_supplied = 'NonProd'
# env_name_supplied = 'PreProd'
# env_name_supplied = 'Dev'
env_name_supplied = 'Personal'
# env_name_supplied = 'Demo'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

# For simple case where MZ=HG
management_zone_host_group_of_same_name_updates = ['Test MZ']

# For case of MZ with more than one HG (or with one HG with a different name)
# management_zone_with_multiple_host_groups_updates = [
#     # ('LCA_PROD_AWS_CallCenter', ['LCA_PROD_AWS_CallCenter-LPK', 'LCA_PROD_AWS_CallCenter-REST', 'LCA_PROD_AWS_CallCenter-UI'])
#     # ('LCA_STAGE_AWS_CallCenter', ['LCA_STAGE_AWS_CallCenter-LPK', 'LCA_STAGE_AWS_CallCenter-REST', 'LCA_STAGE_AWS_CallCenter-UI'])
#     # ('ZZ Contact Center AWS Account', ['LCA_STAGE_AWS_CallCenter-LPK', 'LCA_STAGE_AWS_CallCenter-REST', 'LCA_STAGE_AWS_CallCenter-UI'])
#     ('LCA_PROD_AWS_CallCenter-V2', ['LCA_PROD_AWS_CallCenter-LPK', 'LCA_PROD_AWS_CallCenter-REST', 'LCA_PROD_AWS_CallCenter-UI'])
# ]
management_zone_with_multiple_host_groups_updates = []

object_cache = {}


def add_showcase_rules_to_mz(management_zone_name, host_group_list):
    global object_cache
    endpoint = '/api/config/v1/managementZones'

    if not object_cache.get(endpoint):
        r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
        config_json = r.json()
        config_list = config_json.get('values')
        config_dict = {}
        for config in config_list:
            object_id = copy.deepcopy(config.get('id'))
            name = copy.deepcopy(config.get('name'))
            config_dict[name] = object_id

        object_cache[endpoint] = config_dict

        # print(object_cache)

    additional_dimensional_rules = [
        {
            "appliesTo": "METRIC",
            "conditions": [
                {
                    "conditionType": "METRIC_KEY",
                    "key": "ext:tech.SAP_HANADB",
                    "ruleMatcher": "BEGINS_WITH",
                    "value": None
                }
            ],
            "enabled": True
        },
        {
            "appliesTo": "METRIC",
            "conditions": [
                {
                    "conditionType": "METRIC_KEY",
                    "key": "ext:tech.datapower",
                    "ruleMatcher": "BEGINS_WITH",
                    "value": None
                }
            ],
            "enabled": True
        }
    ]

    object_id = object_cache[endpoint].get(management_zone_name)
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{object_id}', token)
    config_object = r.json()
    new_entity_selector_based_rules = []
    for host_group in host_group_list:
        tag = 'BETA Host Group:' + host_group
        additional_entity_selector_based_rules = get_additional_entity_selector_based_rules(tag)
        new_entity_selector_based_rules.extend(additional_entity_selector_based_rules)

    config_object['name'] = management_zone_name + ' (Full Flow)'
    config_object['dimensionalRules'].extend(additional_dimensional_rules)
    config_object['entitySelectorBasedRules'].extend(new_entity_selector_based_rules)
    config_object.pop('id')

    dynatrace_api.post_object(f'{env}{endpoint}', token, json.dumps(config_object))


def add_database_rule_to_mz(management_zone_name):
    global object_cache
    endpoint = '/api/config/v1/managementZones'

    if not object_cache.get(endpoint):
        r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
        config_json = r.json()
        config_list = config_json.get('values')
        config_dict = {}
        for config in config_list:
            object_id = copy.deepcopy(config.get('id'))
            name = copy.deepcopy(config.get('name'))
            config_dict[name] = object_id

        object_cache[endpoint] = config_dict

    object_id = object_cache[endpoint].get(management_zone_name)
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{object_id}', token)
    config_object = r.json()
    tag = 'Host Group:' + management_zone_name
    current_entity_selector_based_rules = config_object.get('entitySelectorBasedRules')
    additional_entity_selector_based_rule = get_database_entity_selector_based_rule(tag)
    if additional_entity_selector_based_rule not in current_entity_selector_based_rules:
        config_object['entitySelectorBasedRules'].append(additional_entity_selector_based_rule)
        print(f'Adding database rule to {management_zone_name}')
        dynatrace_api.put_object(f'{env}{endpoint}/{object_id}', token, json.dumps(config_object))


def get_database_entity_selector_based_rule(tag):
    database_entity_selector_based_rule = {
            "enabled": True,
            "entitySelector": "type(SERVICE),databaseName.exists(),toRelationships.calls(type(SERVICE),tag({{.tag}}))"
        }

    entity_selector = database_entity_selector_based_rule.get('entitySelector')
    new_entity_selector = entity_selector.replace('{{.tag}}', tag)
    database_entity_selector_based_rule['entitySelector'] = new_entity_selector
    return database_entity_selector_based_rule


def get_additional_entity_selector_based_rules(tag):
    additional_entity_selector_based_rules = [
        {
            "enabled": True,
            "entitySelector": "type(APPLICATION),fromRelationships.calls(type(SERVICE),tag({{.tag}}))"
        },
        {
            "enabled": True,
            "entitySelector": "type(HOST),toRelationships.runsOnHost(type(SERVICE),toRelationships.calls(type(SERVICE),tag({{.tag}})))"
        },
        {
            "enabled": True,
            "entitySelector": "type(HOST),toRelationships.runsOnHost(type(SERVICE),fromRelationships.calls(type(SERVICE),tag({{.tag}})))"
        },
        {
            "enabled": True,
            "entitySelector": "type(SERVICE),toRelationships.calls(type(SERVICE),tag({{.tag}}))"
        },
        {
            "enabled": True,
            "entitySelector": "type(SERVICE),fromRelationships.calls(type(SERVICE),tag({{.tag}}))"
        },
        {
            "enabled": True,
            "entitySelector": "type(PROCESS_GROUP),toRelationships.runsOn(type(SERVICE),fromRelationships.calls(type(SERVICE),tag({{.tag}})))"
        },
        {
            "enabled": True,
            "entitySelector": "type(PROCESS_GROUP),toRelationships.runsOn(type(SERVICE),toRelationships.calls(type(SERVICE),tag({{.tag}})))"
        }
    ]

    new_entity_selector_based_rules = []
    for additional_entity_selector_based_rule in additional_entity_selector_based_rules:
        entity_selector = additional_entity_selector_based_rule.get('entitySelector')
        new_entity_selector = entity_selector.replace('{{.tag}}', tag)
        additional_entity_selector_based_rule['entitySelector'] = new_entity_selector
        new_entity_selector_based_rules.append(additional_entity_selector_based_rule)

    return new_entity_selector_based_rules


def add_showcase_rules():
    for management_zone_host_group_of_same_name in management_zone_host_group_of_same_name_updates:
        add_showcase_rules_to_mz(management_zone_host_group_of_same_name, [management_zone_host_group_of_same_name])

    for management_zone_with_multiple_host_groups_update in management_zone_with_multiple_host_groups_updates:
        management_zone = management_zone_with_multiple_host_groups_update[0]
        host_group_list = management_zone_with_multiple_host_groups_update[1]
        add_showcase_rules_to_mz(management_zone, host_group_list)


def add_database_rules():
    endpoint = '/api/config/v1/managementZones'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    management_zone_json = r.json()
    management_zone_lookup_list = []
    management_zone_list = management_zone_json.get('values')
    for management_zone in management_zone_list:
        management_zone_name = management_zone.get('name')
        management_zone_lookup_list.append(management_zone_name)

    host_group_lookup_list = []
    raw_params = 'pageSize=4000&entitySelector=type(HOST_GROUP)&fields=+properties,+toRelationships&to=-72h'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    endpoint = f'/api/v2/entities?{params}'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    host_group_json = r.json()
    host_group_list = host_group_json.get('entities')
    for host_group in host_group_list:
        host_group_name = host_group.get('displayName')
        host_group_lookup_list.append(host_group_name)

    mz_equal_hg_list = set(management_zone_lookup_list) & set(host_group_lookup_list)

    for mz_equal_hg in sorted(mz_equal_hg_list):
        add_database_rule_to_mz(mz_equal_hg)


def process():
    # For when everything is commented out below...
    pass

    enhancement_type = 'AddShowcaseRules'
    # enhancement_type = 'AddDatabaseRules'

    if enhancement_type == 'AddShowcaseRules':
        add_showcase_rules()
    else:
        if enhancement_type == 'AddDatabaseRules':
            add_database_rules()
        else:
            print('Specify a supported enhancement type and run again')


if __name__ == '__main__':
    process()
