import os
import requests
import ssl
import json

PATH = '../../$Output/Tools/Configs/Saved'

save_config_id = ''
save_config_content = ''
global api
api = ''

supported_environments = {
    'Prod': ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
    'Prep': ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
    'Dev': ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
    'Personal': ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN'),
}

def list_endpoints():
    f = open('config_v1_spec3.json', )
    data = json.load(f)

    paths = data.get('paths')
    endpoints = list(paths.keys())

    for endpoint in endpoints:
        endpoint_dict = paths.get(endpoint)
        methods = list(endpoint_dict.keys())
        if 'get' in methods and str(endpoint).endswith('{id}'):
            print(endpoint[1:].replace('/{id}', ''))


def view_config(config_id, env, token):
    global api
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        url = f'{env}/api/config/v1/{api}/{config_id}'
        print(url)
        r = requests.get(url, headers=headers)
        config_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_config_id
            global save_config_content
            save_config_id = config_id
            save_config_content = config_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400:
                if "The requested configId is invalid" in r.text:
                    print('Config ID not found on this tenant')
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
    global save_config_id
    global save_config_content
    global api

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
    print(f'Enter an Config ID, "ce Prod|Perf|Dev|Personal" to change environments, "l" to list apis, "a <api>" to set an api, "q" to quit, or "s" to save the config just viewed')
    print('')

    while True:
        message = '> '
        input_string = input('%s' % message).rstrip().lstrip()

        if input_string.upper() == 'Q':
            print('Exiting per user request')
            exit()

        if input_string.upper() == 'S':
            global api
            if save_config_id == '':
                print('There is nothing to save yet')
                continue
            else:
                save_path = f'{PATH}/{api}/{env_name}'
                save(save_path, save_config_id + '.json', save_config_content)
                print(f'Saved {save_path}/{save_config_id}.json')
                continue

        if input_string.upper() == 'L':
            list_endpoints()
            continue

        if input_string.upper().startswith('A '):
            api = input_string.split(' ')[1]
            print(f'API set to {api}')
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

        if api == '':
            print('Please use the "a <api>" command to set an API')
            print('Hint: use the "l" command to list APIs and copy one from the list')
            continue

        if ' ' in input_string.rstrip().lstrip():
            print('Invalid command or config id. (Embedded space detected).')
            continue

        config_id = input_string

        # print(env)
        view_config(config_id, env, token)


if __name__ == '__main__':
    run()
