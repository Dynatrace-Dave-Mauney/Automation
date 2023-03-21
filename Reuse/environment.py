import os

# Default name when "get_environment(env_name)" is used
default_friendly_function_name = 'RobotAdmin'

# Support friendly names for frequently used functions.
# Names not found in the list will be handled generically (convert to uppercase and add "_TOKEN")
supported_friendly_function_names = {
    'RobotAdmin': 'ROBOT_ADMIN',
    'TokenManagement': 'TOKEN_MANAGEMENT',
}

# supported_environments = ['Prod', 'Prep', 'Dev', 'Personal', 'FreeTrial1']

def get_environment(env_name):
    return get_environment_for_function(env_name, default_friendly_function_name)


def get_environment_for_function(env_name, friendly_function_name):
    # if env_name not in supported_environments:
    #     print('Error in environment.get_environment(env_name)')
    #     print(f'Invalid environment name: {env_name}')
    #     return None, None, None
    #
    # if friendly_function_name not in supported_friendly_function_names:
    #     print('Error in environment.get_environment_for_function(env_name, friendly_function_name)')
    #     print(f'Invalid friendly function name. Please use one of these supported friendly fuction names: {supported_friendly_function_names}')
    #     return None, None, None

    tenant_key = f'{env_name.upper()}_TENANT'
    print(f'Tenant Key: {tenant_key}')

    if friendly_function_name in supported_friendly_function_names:
        token_key = f'{supported_friendly_function_names.get(friendly_function_name)}_{env_name.upper()}_TOKEN'
    else:
        token_key = f'{friendly_function_name.upper()}_{env_name.upper()}_TOKEN'

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)

    if tenant and token and '.' in token:
        env = f'https://{tenant}.live.dynatrace.com'
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
        print(f'Environment Name: {env_name}')
        print(f'Tenant Key:       {tenant_key}')
        print(f'Environment URL:  {env}')
        print(f'Token:            {masked_token}')
        print(f'Token Function:   {friendly_function_name}')
        print(f'Token Key:        {token_key}')
        return env_name, env, token
    else:
        print('Error in environment.get_environment_for_function(env_name, friendly_function_name)')
        print('Tenant and/or Token environment variable not be populated correctly')
        print(f'Environment Name: {env_name}')
        print(f'Token Function:   {friendly_function_name}')
        print(f'Tenant:           {tenant}')
        if token:
            print(f'Token[0:20]:      {token[0:20]}')
        return env_name, None, None
