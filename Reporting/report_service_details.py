import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    counts_service_type = {}
    counts_service_technology_types = {}
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(SERVICE)&fields=+properties&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    if print_mode:
        print('entityId' + '|' + 'displayName' + '|' + 'detectedName' + '|' + 'serviceType' + '|' + 'listenPorts')
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')

            properties = inner_entities_json.get('properties')

            detected_name = properties.get('detectedName', '')
            service_type = properties.get('serviceType', 'NONE')
            counts_service_type[service_type] = counts_service_type.get(service_type, 0) + 1

            service_technology_types = str(properties.get('serviceTechnologyTypes', 'NONE'))
            service_technology_types = service_technology_types.replace('[', '')
            service_technology_types = service_technology_types.replace(']', '')
            service_technology_types = service_technology_types.replace("'", "")
            counts_service_technology_types[service_technology_types] = counts_service_technology_types.get(service_technology_types, 0) + 1

            if print_mode:
                print(entity_id + '|' + display_name + '|' + detected_name + '|' + service_type + '|' + service_technology_types)

            count_total += 1

    # counts_service_type_str = str(counts_service_type).replace('{', '').replace("'", "").replace('}', '')
    # counts_service_technology_types_str = str(counts_service_technology_types).replace('{', '').replace("'", "").replace('}', '')

    # DEBUG
    # print(counts_service_technology_types)

    counts_service_type_str = sort_and_stringify_dictionary_items(counts_service_type)
    counts_service_technology_types_str = sort_and_stringify_dictionary_items(counts_service_technology_types)

    if print_mode:
        print('Total Services:                  ' + str(count_total))
        print('Service Type Counts:             ' + counts_service_type_str)
        print('Service Technology Types Counts: ' + counts_service_technology_types_str)

    summary.append('There are ' + str(count_total) + ' services currently being monitored.  ')
    if count_total > 0:
        summary.append('The Service Type breakdown is ' + counts_service_type_str + '.  ')
        if count_total > 0:
            summary.append('The Service Technology Type breakdown is ' + counts_service_technology_types_str + '.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def sort_and_stringify_dictionary_items(any_dict):
    dict_str = str(sorted(any_dict.items()))
    dict_str = dict_str.replace('[', '')
    dict_str = dict_str.replace(']', '')
    dict_str = dict_str.replace('), (', '~COMMA~')
    dict_str = dict_str.replace('(', '')
    dict_str = dict_str.replace(')', '')
    dict_str = dict_str.replace(',', ':')
    dict_str = dict_str.replace('~COMMA~', ', ')
    dict_str = dict_str.replace("'", "")
    return dict_str
    

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
