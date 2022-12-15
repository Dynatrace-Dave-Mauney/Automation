import os
import requests
import ssl
import json

selector_file_name = '../../$Test/Tools/Entities/entities.txt'
PATH = '../../$Test/Tools/Entities/saved'

entity_id = ''
entity_content = ''


def view_entity(entity, env, token):
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        r = requests.get(env + '/api/v2/entities/' + entity, headers=headers)
        global entity_content
        entity_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
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
    supported_environments = {
        'Prod': ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
        'Prep': ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
        'Dev': ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
        'Personal': ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN'),
    }

    return supported_environments.get(new_env)


def run():
    global entity_id
    global entity_content

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
            save(PATH, entity_id + '.json', entity_content)
            print(f'Saved {PATH}/{entity_id}.json')
            continue

        if input_string.upper().startswith('CE'):
            env_name, tenant_key, token_key = change_environment(input_string.split(' ')[1])
            tenant = os.environ.get(tenant_key)
            token = os.environ.get(token_key)
            env = f'https://{tenant}.live.dynatrace.com'

            masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

            print(f'Environment Name: {env_name}')
            print(f'Environment:      {env}')
            print(f'Token:            {masked_token}')

            continue

        entity_id = input_string

        print(env)
        view_entity(entity_id, env, token)


if __name__ == '__main__':
    run()
