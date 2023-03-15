# Report on various tagged entities with an emphasis on finding tags that are key-only rather than key/value pairs.

import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    # Skipping for now: 'ESXi', 'AWS', 'Azure scale set', 'Custom device', 'Custom device group'
    taggable_entity_list = [('APPLICATION', 'Applications'), ('SYNTHETIC_TEST', 'Browser Monitors'), ('HTTP_CHECK', 'Http Monitors'), ('SERVICE', 'Services'), ('HOST', 'Hosts'), ('PROCESS_GROUP', 'Process groups'), ('PROCESS_GROUP_INSTANCE', 'Processes')]

    summary = []

    endpoint = '/api/v2/tags'
    
    for taggable_entity in taggable_entity_list:
        count_total = 0
        count_key_only = 0
        count_key_value = 0

        entity_type = taggable_entity[0]
        entity_name = taggable_entity[1]
        
        print('Tags for ' + entity_name)
        
        raw_params = f'entitySelector=type({entity_type})'
        params = urllib.parse.quote(raw_params, safe='/,&=')
        manual_tags_json_list = dynatrace_api.get(env, token, endpoint, params)
    
        if print_mode:
            print('key' + '|' + 'value' + '|' + 'stringRepresentation')
    
        for manual_tags_json in manual_tags_json_list:
            inner_manual_tags_json_list = manual_tags_json.get('tags')
            for inner_manual_tags_json in inner_manual_tags_json_list:
                key = inner_manual_tags_json.get('key', '')
                value = inner_manual_tags_json.get('value', '')
                string_representation = inner_manual_tags_json.get('stringRepresentation', '')
    
                if print_mode:
                    print(key + '|' + value + '|' + string_representation)
    
                count_total += 1
    
                if value == '':
                    count_key_only += 1
                else:
                    count_key_value += 1
    
        if print_mode:
            print('Total Manual Tags: ' + str(count_total))
            print('Key Only:          ' + str(count_key_only))
            print('Key/Value Pairs:   ' + str(count_key_value))
    
        summary.append('There are ' + str(count_total) + ' manual tags currently defined for ' + entity_name + '.  ' +
                       str(count_key_only) + ' are key only and ' + str(count_key_value) + ' are key/value pairs.')

    if print_mode:
        print_list(summary)
        print('Done!')
    
    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        line = line.replace('.  0 are', '.  None are')
        line = line.replace(' 0 are', ' none are')
        print(line)
        

def main():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
