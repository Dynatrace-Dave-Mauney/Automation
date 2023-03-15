import os

supported_environments = {
    'Prod': ('PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
    'Prep': ('PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
    'Dev': ('DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
    'Personal': ('PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN'),
    'FreeTrial1': ('FREETRIAL1_TENANT', 'ROBOT_ADMIN_FREETRIAL1_TOKEN'),
}

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
            return env_name, env, token
        else:
            print('Invalid Environment Configuration!')
            print(f'Set the "env_name ({env_name}), tenant_key ({tenant_key}), token_key ({token_key})" tuple as required and verify the tenant ({tenant}) and token ({token}) environment variables are accessible.')
            exit(1)
