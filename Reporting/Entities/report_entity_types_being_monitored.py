import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    count_monitored_entity_types_total = 0
    count_monitored_total = 0

    endpoint = '/api/v2/entityTypes'
    params = ''
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name' + '|' + 'monitored_count')

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('types')
        for inner_entities_json in inner_entities_json_list:
            # print(inner_entities_json)
            entity_type = inner_entities_json.get('type')
            display_name = inner_entities_json.get('displayName')
            # if entity_type.startswith('cloud:aws'):
            #     print(entity_type + '|' + display_name)
            if True:
                endpoint = '/api/v2/entities'
                entity_selector = 'type(' + entity_type + ')'
                params = '&entitySelector=' + urllib.parse.quote(entity_selector)
                # print(params)
                entity_type_json_list = dynatrace_api.get(env, token, endpoint, params)
                total_count = entity_type_json_list[0].get('totalCount')
                if total_count > 0:
                    print(entity_type + '|' + display_name + '|' + str(total_count))
                    count_monitored_entity_types_total += 1
                    count_monitored_total += total_count

            count_total += 1

    if print_mode:
        print('Total entities defined:       ' + str(count_total))
        print('Total entity types monitored: ' + str(count_monitored_entity_types_total))
        print('Total entities monitored:     ' + str(count_monitored_total))

    summary.append('There are ' + str(count_total) + ' entity types currently defined, ' + str(count_monitored_entity_types_total) + ' entity types being monitored and a total of ' + str(count_monitored_total) + ' entities being monitored.')

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
