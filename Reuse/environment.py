import argparse
import os
import yaml

# Default name when "get_environment(env_name)" is used
default_friendly_function_name = 'DYNATRACE_AUTOMATION'

default_configuration_file = '../$Input/Configurations/configurations.yaml'

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
    # args = sys.argv[1:]
    args = args_parser()

    # if args and args[0] in supported_environments:
    if args.environment_name and args.environment_name in supported_environments:
        print(f'Environment name "{args.environment_name}" was obtained from a command line argument ("-n" or "--environment_name")')
        return args.environment_name
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

    tenant = tenant_key = tenant_source = token = token_key = token_source = None

    args = args_parser()

    if args.environment:
        tenant = args.environment
        tenant_source = 'Command Line Argument "-e" or "--environment"'
    else:
        tenant_key = f'{env_name.upper()}_TENANT'
        # if print_mode:
        #     print(f'Tenant Key: {tenant_key} (from {tenant_source}')
        tenant = os.environ.get(tenant_key)
        tenant_source = f'Environment Variable "{tenant_key}"'

    if args.token:
        token = args.token
        token_source = 'Command Line Argument "-t" or "--token"'
    else:
        if friendly_function_name in supported_friendly_function_names:
            token_key = f'{supported_friendly_function_names.get(friendly_function_name)}_{env_name.upper()}_TOKEN'
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
        # return env_name, None, None
        exit(1)


def get_output_directory_name(default_output_directory):
    args = args_parser()

    if args.output_directory:
        return args.output_directory
    else:
        print('Command lines args do not contain an output directory name')
        print(f'Returning default output directory name of "{default_output_directory}"')
        return default_output_directory


def get_configuration(configuration_key):
    configuration_file = default_configuration_file
    args = args_parser()
    if args.configuration_file:
        configuration_file = args.configuration_file
    else:
        print('Command lines args do not contain a configuration file name')
        print(f'Using default configuration file name of "{default_configuration_file}"')

    yaml_data = read_yaml(configuration_file)
    yaml_value = yaml_data.get(configuration_key)

    return yaml_value


def read_yaml(yaml_file):
    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)


def args_parser():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("-n", "--environment_name", help="environment name ('Prod', 'NonProd', etc.")
    arg_parser.add_argument("-e", "--environment", help="Tenant (such as 'abcd1234' in 'https://abcd1234.live.dynatrace.com")
    arg_parser.add_argument("-t", "--token", help="API Token")
    arg_parser.add_argument("-od", "--output_directory", help="Output directory (rarely used)")
    arg_parser.add_argument("-cf", "--configuration_file", help="Configuration file name.  Used to override the default configuration file name, if needed. (rarely used)")
    arg_parser.add_argument("-of", "--output_file", help="Output file (reserved for future use)")

    args = arg_parser.parse_args()

    # print("args=%s" % args)
    # print("args.environment_name=%s" % args.environment_name)
    # print("args.environment%s" % args.environment)
    # print("args.token=%s" % args.token)
    # print("args.output_directory=%s" % args.output_directory)
    # print("args.output_file=%s" % args.output_file)

    return args
