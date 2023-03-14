# POST auto tags matching the file path pattern to the specified environment.

import json
import glob
import os
import requests
import ssl
import codecs


supported_environments = {
    'Prod': ('PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
    'Prep': ('PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
    'Dev': ('DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
    'Personal': ('PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN'),
    'FreeTrial1': ('FREETRIAL1_TENANT', 'ROBOT_ADMIN_FREETRIAL1_TOKEN'),
}


def run():
    pass
    # upload_auto_tags('Dev', 'uploads/DEV/*.json')


def upload_auto_tags(env_name, path):
    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            auto_tag = f.read()
            auto_tag_json = json.loads(auto_tag)
            auto_tag_id = auto_tag_json.get('id')
            # Remove any id before POST
            if auto_tag_id:
                auto_tag_json.pop('id')
            auto_tag_name = auto_tag_json.get('name')
            print(filename + ': ' + auto_tag_id + ': ' + auto_tag_name)
            env, token = get_environment(env_name)
            post_auto_tag(env, token, auto_tag_id, json.dumps(auto_tag_json))


def get_environment(env_name):
    if env_name not in supported_environments:
        print(f'Invalid environment name: {env_name}')
        return None, None

    tenant_key, token_key = supported_environments.get(env_name)

    if env_name and tenant_key and token_key:
        tenant = os.environ.get(tenant_key)
        token = os.environ.get(token_key)
        env = f'https://{tenant}.live.dynatrace.com'

        if tenant and token and '.' in token:
            masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
            print(f'Environment Name: {env_name}')
            print(f'Environment:      {env}')
            print(f'Token:            {masked_token}')
            return env, token
        else:
            print('Invalid Environment Configuration!')
            print(f'Set the "env_name ({env_name}), tenant_key ({tenant_key}), token_key ({token_key})" tuple as required and verify the tenant ({tenant}) and token ({token}) environment variables are accessible.')
            exit(1)


def post_auto_tag(env, token, auto_tag_id, payload):
    url = env + '/api/config/v1/autoTags/'
    print('post: ' + url)
    try:
        r = requests.post(url, payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        # If you need to bypass certificate checks on managed and are ok with the risk:
        # r = requests.post(url, payload, headers=HEADERS, verify=False)
        if r.status_code not in [200, 201, 204]:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
    except ssl.SSLError:
        print('SSL Error')


if __name__ == '__main__':
    run()
