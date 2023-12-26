import argparse
import os
import yaml

# default_configuration_file = '../$Input/Configurations/configurations.yaml'
default_configuration_file = 'C:\\Users\\dave.mauney\\PycharmProjects\\Automation\\$Input\\Configurations\\configurations.yaml'

# Support friendly names for frequently used functions.
# Names not found in the list will be handled generically by
#   converting to uppercase
#   replacing spaces with underscores
#   appending "_TOKEN")
# The below should be considered deprecated:
# In the future use "Dynatrace Automation" for generic token for all Automation,
# or "Dynatrace Automation <SubProject>" for a more specific token:
# Examples:
# Dynatrace Automation
# Dynatrace Automation Reporting
# Dynatrace Automation Reporting Deployment
# Dynatrace Automation Tools
# Dynatrace Automation Token Management
# Dynatrace Platform Document

supported_environments = ['Prod', 'NonProd', 'Prep', 'Dev', 'Personal', 'Demo']


def get_env_name(function_name):
    # args = sys.argv[1:]
    args = args_parser()

    # if args and args[0] in supported_environments:
    if args.environment_name and args.environment_name in supported_environments:
        print(f'Environment name "{args.environment_name}" was obtained from a command line argument ("-n" or "--environment_name")')
        return args.environment_name
    else:
        if function_name:
            function_name = function_name.upper().replace(' ', '_')
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


# get_client* methods are for the "new platform"
def get_client_environment(env_name):
    default_friendly_function_name = 'DYNATRACE_API_CLIENT'
    return get_client_environment_for_function(env_name, default_friendly_function_name)


def get_client_environment_for_function(env_name, friendly_function_name):
    return get_client_environment_for_function_print_control(env_name, friendly_function_name, True)


def get_client_environment_for_function_print_control(env_name, friendly_function_name, print_mode):
    # Use this method for control over print statements.
    # The norm is to call "get_client_environment_for_function(env_name, friendly_function_name)" or
    # "get_client_environment(env_name)" for maximum convenience and with print on.
    # But when print needs to be off, use this method directly.

    tenant_key = client_id_key = client_secret_key = None

    args = args_parser()

    if args.environment:
        tenant = args.environment
        tenant_source = 'Command Line Argument "-e" or "--environment"'
    else:
        tenant_key = f'{env_name.upper()}_TENANT'
        tenant = os.environ.get(tenant_key)
        tenant_source = f'Environment Variable "{tenant_key}"'

    if args.client_id:
        client_id = args.client_id
        client_id_source = 'Command Line Argument "-ci" or "--client_id"'
    else:
        client_id_key = f'{friendly_function_name.upper().replace(" ", "_")}_{env_name.upper()}_CLIENT_ID'
        client_id = os.environ.get(client_id_key)
        client_id_source = f'Environment Variable "{client_id_key}"'

    if args.client_secret:
        client_secret = args.client_secret
        client_secret_source = 'Command Line Argument "-cs" or "--client_secret"'
    else:
        client_secret_key = f'{friendly_function_name.upper().replace(" ", "_")}_{env_name.upper()}_CLIENT_SECRET'
        client_secret = os.environ.get(client_secret_key)
        client_secret_source = f'Environment Variable "{client_secret_key}"'

    if tenant and client_id and client_secret and '.' in client_id and '.' in client_secret:
        env = f'https://{tenant}.apps.dynatrace.com'
        masked_client_secret = f"{client_secret.split('.')[0]}.{client_secret.split('.')[1]}.{client_secret.split('.')[2][0:10]}* (Masked)"
        if print_mode:
            print(f'Environment Name:  {env_name}')
            print(f'Environment URL:   {env} (from {tenant_source})')
            print(f'Client ID:         {client_id} (from {client_id_source})')
            print(f'Client Secret:     {masked_client_secret} (from {client_secret_source})')
            print(f'Function:          {friendly_function_name}')
            if tenant_key:
                print(f'Tenant Key:        {tenant_key}')
            if client_id_key:
                print(f'Client ID Key:     {client_id_key}')
            if client_secret_key:
                print(f'Client Secret Key: {client_secret_key}')
        return env_name, env, client_id, client_secret
    else:
        if print_mode:
            print('Error in environment.get_client_environment_for_function_print_control(env_name, friendly_function_name, print_mode)')
            print('Client ID and/or Client Secret variable not populated correctly')
            print(f'Environment Name: {env_name}')
            print(f'Function:         {friendly_function_name}')
            if tenant:
                print(f'Tenant:              {tenant}')
            if client_id:
                print(f'Client ID:           {client_id[0:20]}')
            if client_secret:
                print(f'Client Secret[0:20]: {client_id[0:20]}')
            if tenant_key:
                print(f'Tenant Key:          {tenant_key}')
            if client_id_key:
                print(f'Client ID Key:       {client_id_key}')
            if client_secret_key:
                print(f'Client Secret Key:   {client_secret_key}')
        exit(1)


def get_environment(env_name):
    default_friendly_function_name = 'DYNATRACE_AUTOMATION'
    return get_environment_for_function(env_name, default_friendly_function_name)


def get_environment_for_function(env_name, friendly_function_name):
    return get_environment_for_function_print_control(env_name, friendly_function_name, True)


def get_environment_for_function_print_control(env_name, friendly_function_name, print_mode):
    # Use this method for control over print statements.
    # The norm is to call "get_environment_for_function(env_name, friendly_function_name)" or
    # "get_environment(env_name)" for maximum convenience and with print on.
    # But when print needs to be off, use this method directly.

    # tenant = tenant_key = tenant_source = token = token_key = token_source = None
    tenant_key = token_key = None

    args = args_parser()

    if args.environment:
        tenant = args.environment
        tenant_source = 'Command Line Argument "-e" or "--environment"'
    else:
        tenant_key = f'{env_name.upper()}_TENANT'
        tenant = os.environ.get(tenant_key)
        tenant_source = f'Environment Variable "{tenant_key}"'

    if args.token:
        token = args.token
        token_source = 'Command Line Argument "-t" or "--token"'
    else:
        token_key = f'{friendly_function_name.upper().replace(" ", "_")}_{env_name.upper()}_TOKEN'
        token = os.environ.get(token_key)
        token_source = f'Environment Variable "{token_key}"'

    if tenant and token and '.' in token:
        env = f'https://{tenant}.live.dynatrace.com'
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
        if print_mode:
            print(f'Environment Name: {env_name}')
            print(f'Environment URL:  {env} (from {tenant_source})')
            print(f'Token:            {masked_token} (from {token_source})')
            print(f'Token Function:   {friendly_function_name}')
            if tenant_key:
                print(f'Tenant Key:       {tenant_key}')
            if token_key:
                print(f'Token Key:        {token_key}')
        return env_name, env, token
    else:
        if print_mode:
            print('Error in environment.get_environment_for_function(env_name, friendly_function_name)')
            print('Tenant and/or Token environment variable not populated correctly')
            print(f'Environment Name: {env_name}')
            print(f'Token Function:   {friendly_function_name}')
            if tenant:
                print(f'Tenant:           {tenant}')
            if token:
                print(f'Token[0:20]:      {token[0:20]}')
            if tenant_key:
                print(f'Tenant Key:       {tenant_key}')
            if token_key:
                print(f'Token Key:        {token_key}')
        exit(1)


def get_output_directory_name(default_output_directory):
    args = args_parser()

    if args.output_directory:
        return os.path.abspath(args.output_directory)
    else:
        # print('Command lines args do not contain an output directory name')
        # print(f'Returning default output directory name of "{default_output_directory}"')
        return os.path.abspath(default_output_directory)


def get_boolean_environment_variable(key, default_value):
    environment_variable_value = os.getenv(key, default_value)
    if environment_variable_value.lower() in ['true', 'yes', 'on']:
        return True
    else:
        return False


def get_configuration(configuration_key, **kwargs):
    configuration_file = kwargs.get('configuration_file')

    # Configuration file path order of precedence:
    # 1. Method Argument
    # 2. Command line argument
    # 3. Environment variable
    if not configuration_file:
        args = args_parser()
        if args.configuration_file:
            configuration_file = args.configuration_file
        else:
            config_file_environment_variable_key = 'DYNATRACE_AUTOMATION_CONFIG_FILE'
            configuration_file = os.getenv(config_file_environment_variable_key, default_configuration_file)
            if not configuration_file:
                print(f'Neither "configuration_file" method argument or command line argument, or environment variable {config_file_environment_variable_key} contain a configuration file name')
                print(f'Using default configuration file name of "{default_configuration_file}"')

    yaml_data = read_yaml(configuration_file)

    if yaml_data:
        yaml_value = yaml_data.get(configuration_key)
        return yaml_value
    else:
        return None


def read_yaml(yaml_file):
    try:
        with open(yaml_file, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return None


def args_parser():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("-n", "--environment_name", help="environment name ('Prod', 'NonProd', etc.")
    arg_parser.add_argument("-e", "--environment", help="Tenant (such as 'abcd1234' in 'https://abcd1234.live.dynatrace.com")
    arg_parser.add_argument("-t", "--token", help="API Token")
    arg_parser.add_argument("-ci", "--client_id", help="Client ID")
    arg_parser.add_argument("-cs", "--client_secret", help="Client Secret")
    arg_parser.add_argument("-od", "--output_directory", help="Output directory (rarely used)")
    arg_parser.add_argument("-cf", "--configuration_file", help="Configuration file name.  Used to override the default configuration file name, if needed. (rarely used)")
    arg_parser.add_argument("-of", "--output_file", help="Output file (reserved for future use)")

    args = arg_parser.parse_args()

    return args
