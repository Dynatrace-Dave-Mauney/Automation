import os
import requests
import ssl
import json

PATH = '../../$Output/Tools/Events/Saved'

save_event_id = ''
save_event_content = ''

supported_environments = {
    'Prod': ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
    'Prep': ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
    'Dev': ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
    'Personal': ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN'),
}


def view_event(event_id, env, token):
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        r = requests.get(env + '/api/v2/events/' + event_id, headers=headers)
        event_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            global save_event_id
            global save_event_content
            save_event_id = event_id
            save_event_content = event_content
            print(json.dumps(r.json(), indent=4))
        else:
            if r.status_code == 400:
                if "The requested eventId is invalid" in r.text:
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
    global save_event_id
    global save_event_content

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
    print(f'Enter an Event ID, "ce Prod|Perf|Dev|Personal" to change environments, "q" to quit, or "s" to save the event just viewed')
    print(f'HINT: Use "report_events.py" to list Event IDs')
    print('')

    while True:
        message = '> '
        input_string = input('%s' % message).rstrip().lstrip()

        if input_string.upper() == 'Q':
            print('Exiting per user request')
            exit()

        if input_string.upper() == 'S':
            save_path = PATH + '/' + env_name
            save(save_path, save_event_id + '.json', save_event_content)
            print(f'Saved {save_path}/{save_event_id}.json')
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
            print('Invalid command or event id. (Embedded space detected).')
            continue

        event_id = input_string

        # print(env)
        view_event(event_id, env, token)


if __name__ == '__main__':
    run()
