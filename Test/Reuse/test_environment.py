import sys

# Support import from "Reuse" package when invoked from command line
sys.path.append("../..")

from Reuse import environment


def test_environment():
    print('Test get_environment(env_name)')
    env_name, env, token = environment.get_environment('Dev')
    if token:
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
    else:
        masked_token = None
    print(f'Returned values: {env_name}, {env}, {masked_token}')
    print('')

    print('Test get_environment_for_function(env_name, friendly_function_name) - RobotAdmin')
    env_name, env, token = environment.get_environment_for_function('Dev', 'RobotAdmin')
    if token:
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
    else:
        masked_token = None
    print('')
    print(f'Returned values: {env_name}, {env}, {masked_token}')
    print('')

    print('Test get_environment_for_function(env_name, friendly_function_name) - TokenManagement')
    env_name, env, token = environment.get_environment_for_function('Dev', 'TokenManagement')
    if token:
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
    else:
        masked_token = None
    print('')
    print(f'Returned values: {env_name}, {env}, {masked_token}')
    print('')

    print('Test get_environment_for_function(env_name, friendly_function_name) - Arbitrary (Environment Variables Exist)')
    env_name, env, token = environment.get_environment_for_function('Dev', 'Robot_Admin')
    if token:
        masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
    else:
        masked_token = None
    print('')
    print(f'Returned values: {env_name}, {env}, {masked_token}')
    print('')

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
