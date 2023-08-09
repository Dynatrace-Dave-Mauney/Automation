import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    print('Hosts with no management zone')
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,managementZones'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    print('entityId' + '|' + 'displayName')
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            management_zones = inner_entities_json.get('managementZones')
            if not management_zones or management_zones == []:
                properties = inner_entities_json.get('properties')
                is_monitoring_candidate = properties.get('isMonitoringCandidate', False)
                if not is_monitoring_candidate:
                    entity_id = inner_entities_json.get('entityId', '')
                    display_name = inner_entities_json.get('displayName', '')
                    print(entity_id + '|' + display_name)
def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)
    
    
if __name__ == '__main__':
    main()
