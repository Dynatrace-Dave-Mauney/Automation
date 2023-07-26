import sys


# Support import from "Reuse" package when invoked from command line
# sys.path.append("../..")

from Reuse import environment


def test_environment():
    print('Test args_parser()')
    print(sys.argv)
    # Examples:
    # -n Prod -e pey66649 -t xxx -od /output_dir -of outfile.txt
    # --environment_name Prod --environment pey66649 --token xxx --output_directory /output_dir --output_file outfile.txt
    args = environment.args_parser()
    print("args=%s" % args)
    print("args.environment_name=%s" % args.environment_name)
    print("args.environment%s" % args.environment)
    print("args.token=%s" % args.token)
    print("args.output_directory=%s" % args.output_directory)
    print("args.output_file=%s" % args.output_file)
    print('')

    # Cheesy way to test:  use IDE configuration to set args as needed or leave them off entirely.
    print('Test get_output_directory()')
    output_directory = environment.get_output_directory_name('/tmp')
    print(f'Returned output directory value: {output_directory}')
    print('')

    print('Test get_env_name()')
    env_name = environment.get_env_name('RobotAdmin')
    print(f'Returned value: {env_name}')
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

    #
    #
    # Run last as it fails and exits!!!
    #
    #
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
