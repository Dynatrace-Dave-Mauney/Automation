import sys

# Support import from "Reuse" package when invoked from command line
sys.path.append("../..")

from Reuse import environment


def test_environment():
    # Cheesy way to test:  use IDE configuration to set args as needed or leave them off entirely.
    # This method is tested first because the last test causes an exit, so it makes sense here
    print('Test get_output_directory()')
    output_directory = environment.get_output_directory_name()
    print(f'Returned output directory value: {output_directory}')
    print('')

    print('Test get_environment(env_name)')
    env_name, env, token = environment.get_environment('NonProd')
    if token:
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
    else:
        masked_token = None
    print(f'Returned values: {env_name}, {env}, {masked_token}')
    print('')

    print('Test get_environment_for_function(env_name, friendly_function_name) - Dynatrace Automation')
    env_name, env, token = environment.get_environment_for_function('NonProd', 'Dynatrace Automation')
    if token:
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
    else:
        masked_token = None
    print('')
    print(f'Returned values: {env_name}, {env}, {masked_token}')
    print('')

    print('Test get_environment_for_function(env_name, friendly_function_name) - Dynatrace Automation Token Management')
    env_name, env, token = environment.get_environment_for_function('NonProd', 'Dynatrace Automation Token Management')
    if token:
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
    else:
        masked_token = None
    print('')
    print(f'Returned values: {env_name}, {env}, {masked_token}')
    print('')

    print('Test get_environment_for_function(env_name, friendly_function_name) - Arbitrary (Environment Variables Exist)')
    env_name, env, token = environment.get_environment_for_function('NonProd', 'Dynatrace Automation')
    if token:
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
    else:
        masked_token = None
    print('')
    print(f'Returned values: {env_name}, {env}, {masked_token}')
    print('')

    # Run last as it fails!
    print('Test get_environment_for_function(env_name, friendly_function_name) - Arbitrary (Environment Variables Do Not Exist)')
    env_name, env, token = environment.get_environment_for_function('Foo', 'Bar')
    if token:
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
    else:
        masked_token = None
    print('')
    print(f'Returned values: {env_name}, {env}, {masked_token}')
    print('')

if __name__ == '__main__':
    test_environment()
