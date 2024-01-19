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
    hosts = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    return hosts


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


def main():
    friendly_function_name = 'Dynatrace Automation Tools'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    print('Hosts monitored by OneAgent')

    process(env, token, True)


if __name__ == '__main__':
    main()
