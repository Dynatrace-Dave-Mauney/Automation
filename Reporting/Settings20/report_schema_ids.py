from Reuse import dynatrace_api
from Reuse import environment


def process():
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

    endpoint = '/api/v2/settings/schemas'
    params = ''
    settings_json_list = dynatrace_api.get(env, token, endpoint, params)

    schema_ids = []
    schema_dict = {}

    for settings_json in settings_json_list:
        inner_settings_json_list = settings_json.get('items')
        for inner_settings_json in inner_settings_json_list:
            schema_id = inner_settings_json.get('schemaId')
            schema_ids.append(schema_id)
            latest_schema_version = inner_settings_json.get('latestSchemaVersion')
            schema_dict[schema_id] = latest_schema_version

    for schema_id in sorted(schema_ids):
        print(schema_id)


if __name__ == '__main__':
    process()
