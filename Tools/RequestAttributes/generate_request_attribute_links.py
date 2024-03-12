from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    endpoint = '/api/config/v1/service/requestAttributes'
    request_attributes_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for request_attributes_json in request_attributes_json_list:
        inner_request_attributes_json_list = request_attributes_json.get('values')
        for inner_request_attributes_json in inner_request_attributes_json_list:
            entity_id = inner_request_attributes_json.get('id')
            # if entity_id.startswith('aaaaaaaa-bbbb-cccc-dddd-1'):
            # if entity_id.startswith('aaaaaaaa-bbbb-cccc-dddd-2'):
            # if entity_id.startswith('aaaaaaaa-bbbb-cccc-dddd-3'):
            # if entity_id.startswith('aaaaaaaa-bbbb-cccc-dddd-9'):
            if entity_id.startswith('aaaaaaaa-bbbb-cccc-dddd-9'):
                name = inner_request_attributes_json.get('name').replace('(', '%28').replace(')','%29')
                # print(env, name, entity_id)
                print(f'{env}/ui/diagnostictools/mda?gtf=-24h%20to%20now&metric=REQUEST_COUNT&dimension=%7BRequest:Name%7D%20%7BRequestAttribute:{name}%7D&mergeServices=true&aggregation=COUNT&servicefilter=0%1E15%11{entity_id}')


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
