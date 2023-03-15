import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    count_total_hosts_in_groups = 0

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST_GROUP)&fields=+properties,+toRelationships&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=?')

    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    if print_mode:
        print('entityId' + '|' + 'displayName' + '|' + 'detectedName' + '|' + 'Hosts In Group')
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')

            properties = inner_entities_json.get('properties')
            detected_name = properties.get('detectedName', '')
            to_relationships = inner_entities_json.get('toRelationships')
            if to_relationships:
                hosts_in_group = len(to_relationships.get('isInstanceOf', []))
            else:
                hosts_in_group = 0

            hosts_in_group_str = str(hosts_in_group)

            if print_mode:
                print(entity_id + '|' + display_name + '|' + detected_name + '|' + hosts_in_group_str)

            count_total += 1
            count_total_hosts_in_groups = count_total_hosts_in_groups + hosts_in_group

    if print_mode:
        print('Total Host Groups:          ' + str(count_total))
        print('Total Hosts in Host Groups: ' + str(count_total_hosts_in_groups))

    summary.append('There are ' + str(count_total) + ' hosts groups currently defined.  ')
    if count_total > 0:
        summary.append(str(count_total_hosts_in_groups) + ' hosts currently belong to a host group.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
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
