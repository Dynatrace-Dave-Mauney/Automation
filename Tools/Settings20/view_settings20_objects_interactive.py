import os
import requests
import ssl
import json

PATH = '../../$Output/Tools/Settings20/Saved'

save_object_id = ''
save_object_content = ''

supported_environments = {
    'Prod': ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
    'Prep': ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
    'Dev': ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
    'Personal': ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN'),
}


def view_object(object_id, env, token):
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        r = requests.get(env + '/api/v2/settings/objects/' + object_id, headers=headers)
        object_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_object_id
            global save_object_content
            save_object_id = object_id
            save_object_content = object_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400 and "Could not decode" in r.text:
                print('Could not decode the Object ID')
            else:
                if r.status_code == 404 and "not found" in r.text:
                    print('Object ID not found on this tenant')
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
    global save_object_id
    global save_object_content

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
    print(f'Enter an Object ID, "ce Prod|Perf|Dev|Personal" to change environments, "q" to quit, or "s" to save the object just viewed')
    print('')

    while True:
        message = '> '
        input_string = input('%s' % message).rstrip().lstrip()

        if input_string.upper() == 'Q':
            print('Exiting per user request')
            exit()

        if input_string.upper() == 'S':
            save_path = PATH + '/' + env_name
            save(save_path, save_object_id + '.json', save_object_content)
            print(f'Saved {save_path}/{save_object_id}.json')
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
            print('Invalid command or object id. (Embedded space detected).')
            continue

        view_object(input_string, env, token)


if __name__ == '__main__':
    run()
