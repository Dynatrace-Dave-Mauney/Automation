import os
import sys

# Default name when "get_environment(env_name)" is used
default_friendly_function_name = 'DYNATRACE_AUTOMATION'

# Support friendly names for frequently used functions.
# Names not found in the list will be handled generically by
#   converting to uppercase
#   replacing spaces with underscores
#   appending "_TOKEN")
# The below should be considered deprecated:
# In the future use "Dynatrace Automation" for generic token for all Automation,
# or "Dynatrace Automation <SubProject>" for a more specific token:
# Examples:
# Dynatrace Automation Reporting
# Dynatrace Automation Tools
# Dynatrace Automation Token Management
supported_friendly_function_names = {
    'RobotAdmin': 'ROBOT_ADMIN',
}

supported_environments = ['Prod', 'NonProd', 'Prep', 'Dev', 'Personal', 'FreeTrial1']


def get_env_name(function_name):
    args = sys.argv[1:]
    if args and args[0] in supported_environments:
        print(f'Environment name "{args[0]}" was obtained from a command line argument')
        return(args[0])
    else:
        if function_name:
            if function_name not in supported_friendly_function_names:
                function_name = function_name.upper().replace(' ', '_')
            else:
                function_name = supported_friendly_function_names.get(function_name)
        else:
            function_name = ''
        environment_variable_key = f'{function_name.upper()}_ENV_NAME'
        env_name = os.getenv(environment_variable_key)
        if env_name:
            print(f'Environment name "{env_name}" was obtained from the environment variable "{environment_variable_key}"')
            return env_name
        else:
            print(f'CAUTION: Environment name not supplied via command line argument or environment variable "{environment_variable_key}", so "Default" is being used!')
            return 'Default'


def get_environment(env_name):
    return get_environment_for_function(env_name, default_friendly_function_name)


def get_environment_for_function(env_name, friendly_function_name):
    return get_environment_for_function_print_control(env_name, friendly_function_name, True)


def get_environment_for_function_print_control(env_name, friendly_function_name, print_mode):
    # Use this method for control over print statements.
    # The norm is to call "get_environment_for_function(env_name, friendly_function_name)" or
    # "get_environment(env_name)" for maximum convenience and with print on.
    # But when print needs to be off, use this method directly.

    tenant_key = f'{env_name.upper()}_TENANT'
    if print_mode:
        print(f'Tenant Key: {tenant_key}')

    if friendly_function_name in supported_friendly_function_names:
        token_key = f'{supported_friendly_function_names.get(friendly_function_name)}_{env_name.upper()}_TOKEN'
    else:
        token_key = f'{friendly_function_name.upper().replace(" ", "_")}_{env_name.upper()}_TOKEN'

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)

    if tenant and token and '.' in token:
        env = f'https://{tenant}.live.dynatrace.com'
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
        if print_mode:
            print(f'Environment Name: {env_name}')
            print(f'Tenant Key:       {tenant_key}')
            print(f'Environment URL:  {env}')
            print(f'Token:            {masked_token}')
            print(f'Token Function:   {friendly_function_name}')
            print(f'Token Key:        {token_key}')
        return env_name, env, token
    else:
        if print_mode:
            print('Error in environment.get_environment_for_function(env_name, friendly_function_name)')
            print('Tenant and/or Token environment variable not populated correctly')
            print(f'Environment Name: {env_name}')
            print(f'Token Function:   {friendly_function_name}')
            print(f'Token Key:        {token_key}')
        if tenant and print_mode:
            print(f'Tenant:           {tenant}')
        if token and print_mode:
            print(f'Token[0:20]:      {token[0:20]}')
        # return env_name, None, None
        exit(1)

def get_output_directory_name():
    args = sys.argv[1:]
    if args and args[0] in supported_environments and args[1]:
        return(args[1])
    else:
        print('Command lines args do not contain a supported environment and output directory name')
        print('Returning default output directory name of "."')
        return '.'