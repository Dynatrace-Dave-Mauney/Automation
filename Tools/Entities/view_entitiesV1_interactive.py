import os
import requests
import ssl
import json

PATH = '../../$Output/Tools/EntitiesV1/Saved'

save_entity_id = ''
save_entity_content = ''

supported_environments = {
    'Prod': ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
    'Prep': ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
    'Dev': ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
    'Personal': ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN'),
}


def view_entity(entity_id, env, token):
    entity_endpoints = {
        'APPLICATION': 'entity/applications',
        # 'CUSTOM_DEVICE': 'entity/infrastructure/custom',
        'HOST': 'entity/infrastructure/hosts',
        'HTTP_CHECK': 'synthetic/monitors',
        'PROCESS_GROUP': 'entity/infrastructure/process-groups',
        'PROCESS_GROUP_INSTANCE': 'entity/infrastructure/processes',
        'SERVICE': 'entity/services',
        'SYNTHETIC_TEST': 'synthetic/monitors',
    }

    headers = {'Authorization': 'Api-Token ' + token}

    entity_type = entity_id.split('-')[0]

    entity_endpoint = entity_endpoints.get(entity_type)

    if not entity_endpoint:
        print(f'Entity type not supported: {entity_type}')
        print(f'Supported Entities: {entity_endpoints.keys()}')
        return

    try:
        url = f'{env}/api/v1/{entity_endpoint}/{entity_id}'
        print(url)
        r = requests.get(url, headers=headers)
        entity_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_entity_id
            global save_entity_content
            save_entity_id = entity_id
            save_entity_content = entity_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400:
                if "The requested entityId is invalid" in r.text:
                    print('Entity ID not found on this tenant')
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def save(path, file, content):
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + "/" + file, "w", encoding='utf8') as text_file:
        text_file.write("%s" % content)


def change_environment(new_env):
    if new_env not in supported_environments:
        print('Invalid Environment Name...')
        return new_env, 'INVALID', 'NA'

    return supported_environments.get(new_env)


def run():
    global save_entity_id
    global save_entity_content

    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

    print(f'Environment Name: {env_name}')
    print(f'Environment:      {env}')
    print(f'Token:            {masked_token}')

    print('')
    print(f'Enter an Entity ID, "ce Prod|Perf|Dev|Personal" to change environments, "q" to quit, or "s" to save the entity just viewed')
    print('')

    while True:
        message = '> '
        input_string = input('%s' % message).rstrip().lstrip()

        if input_string.upper() == 'Q':
            print('Exiting per user request')
            exit()

        if input_string.upper() == 'S':
            save_path = PATH + '/' + env_name
            save(save_path, save_entity_id + '.json', save_entity_content)
            print(f'Saved {save_path}/{save_entity_id}.json')
            continue

        if input_string.upper().startswith('CE '):
            new_env = input_string.split(' ')[1]

            if new_env not in supported_environments:
                print('Invalid Environment Name...')
                continue

            env_name, tenant_key, token_key = change_environment(new_env)
            tenant = os.environ.get(tenant_key)
            token = os.environ.get(token_key)
            env = f'https://{tenant}.live.dynatrace.com'

            masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

            print(f'Environment Name: {env_name}')
            print(f'Environment:      {env}')
            print(f'Token:            {masked_token}')

            continue

        if ' ' in input_string.rstrip().lstrip():
            print('Invalid command or entity id. (Embedded space detected).')
            continue

        entity_id = input_string

        # print(env)
        view_entity(entity_id, env, token)


if __name__ == '__main__':
    run()
