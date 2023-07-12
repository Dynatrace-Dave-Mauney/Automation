import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(SYNTHETIC_TEST)&fields=+properties,+toRelationships&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    if print_mode:
        print('entityId' + '|' + 'displayName' + '|' + 'detectedName' + '|' + 'Number of Steps')
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')

            properties = inner_entities_json.get('properties')
            number_of_steps = "0"
            detected_name = properties.get('detectedName', '')
            to_relationships = inner_entities_json.get('toRelationships')
            if to_relationships:
                number_of_steps = str(len(to_relationships.get('isStepOf')))

            if print_mode:
                print(entity_id + '|' + display_name + '|' + detected_name + '|' + number_of_steps)

            count_total += 1

    if print_mode:
        print('Total Synthetic Tests (Browser): ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' browser synthetic tests currently defined and reporting data.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)
        

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
    process(env, token, True)
    
    
if __name__ == '__main__':
    main()
