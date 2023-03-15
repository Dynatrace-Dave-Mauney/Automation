import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token, print_mode):
    detected_host_name_list = []

    hosts = get_hosts(env, token)
    for entities in hosts:
        total_count = int(entities.get('totalCount'))
        if total_count > 0:
            host_entities = entities.get('entities')
            for host_json in host_entities:
                display_name = host_json.get('displayName', '')
                detected_name = host_json.get('properties').get('detectedName', '')
                # print(f'{detected_name}: {display_name}')
                if detected_name == '':
                    detected_host_name_list.append(display_name.lower())
                else:
                    detected_host_name_list.append(detected_name.lower())

    host_name_list = remove_duplicates(sorted(detected_host_name_list))

    if print_mode:
        for host_name in host_name_list:
            print(host_name)

    return host_name_list


def get_hosts(env, token):
    # print(f'get_entity_types({env}, {token})')
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=500&entitySelector=type(HOST)&fields=+properties.detectedName'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    hosts = dynatrace_api.get(env, token, endpoint, params)
    return hosts


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


def main():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    print('Hosts monitored by OneAgent')

    process(env, token, True)


if __name__ == '__main__':
    main()
