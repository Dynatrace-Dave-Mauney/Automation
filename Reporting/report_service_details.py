import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    counts_service_type = {}
    counts_service_technology_types = {}
    endpoint = '/api/v2/entities'
    params = 'pageSize=4000&entitySelector=type%28%22service%22%29&fields=%2Bproperties&to=-5m'
    entities_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)
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
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, True)


if __name__ == '__main__':
    # print('Not to be run standalone.  Use one of the "perform_*.py" modules to run this module.')
    # exit(1)
    main()
