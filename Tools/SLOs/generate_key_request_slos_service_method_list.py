import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    print('')
    print('Copy the following lines into configurations.yaml, and modify as needed...')
    print('')
    print('target_env_name: "Personal"')
    print('')
    print('slo_name_prefix: "Personal"')
    print('')
    print('slo_evaluation_window: "-28d"')
    print('')
    print('service_method_list:')
    print('  [')
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(SERVICE_METHOD),mzName("App: KEEP - PROD")&fields=+properties&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            print(f"    ['{display_name}', '{entity_id}'],")

    print(']')


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
