import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token, print_mode):
    url_reference_list = process_entity_type(env, token)

    if print_mode:
        for url_reference in url_reference_list:
            print(url_reference)

    return url_reference_list


def process_entity_type(env, token):
    url_list = []
    endpoint = '/api/v1/synthetic/monitors'
    raw_params = 'enabled=true'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    synthetics_json_list = dynatrace_api.get(env, token, endpoint, params)
    for synthetics_json in synthetics_json_list:
        inner_synthetics_json_list = synthetics_json.get('monitors')
        for inner_synthetics_json in inner_synthetics_json_list:
            endpoint = '/api/v1/synthetic/monitors/' + inner_synthetics_json.get('entityId')
            synthetic_json = dynatrace_api.get(env, token, endpoint, params)[0]
            synthetic_name = synthetic_json.get('name')
            synthetic_type = synthetic_json.get('type')
            if synthetic_type == 'BROWSER':
                step_key = 'events'
            else:
                step_key = 'requests'
            script_events = synthetic_json.get('script').get(step_key)
            for script_event in script_events:
                url = script_event.get('url')
                url_reference = f'{url} referenced by {synthetic_name} ({synthetic_type})'
                if url:
                    # if 'https' not in url.lower():
                    #     print(f'NON-HTTPS URL: {url}')
                    url_list.append(url_reference)

    return remove_duplicates(sorted(url_list))


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
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    print('URLs referenced by Synthetics')
    process(env, token, True)


if __name__ == '__main__':
    main()
