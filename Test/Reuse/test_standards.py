from Reuse import environment
from Reuse import standards


def test_standards():
    env_name, env, configuration_object = get_env()
    print('Environment Name, Tenant and Configuration Object:', env_name, env, configuration_object)

    valid_names = environment.get_configuration(f'test_standards.valid_names_{env_name}', configuration_object=configuration_object)
    print('Valid Names:', valid_names)
    for valid_name in valid_names:
        test_check_naming_standard(env_name, valid_name, configuration_object, 'management zone')
    print('')

    valid_names = environment.get_configuration(f'test_standards.valid_host_group_names_{env_name}', configuration_object=configuration_object)
    print('Valid Host Group Names:', valid_names)
    for valid_name in valid_names:
        test_check_naming_standard(env_name, valid_name, configuration_object, 'host group')
    print('')

    invalid_names = environment.get_configuration(f'test_standards.invalid_names_{env_name}', configuration_object=configuration_object)
    print('Invalid Names:', invalid_names)
    for invalid_name in invalid_names:
        test_check_naming_standard(env_name, invalid_name, configuration_object, 'management zone')
    print('')


def test_check_naming_standard(env, name, configuration_object, entity_type):
    print(f'test_check_naming_standard({env},{name})')
    standard_met, reason = standards.check_naming_standard(env, name, configuration_object, entity_type)
    if standard_met:
        print(f'PASS: {env},{name}')
    else:
        print(f'FAIL: {env},{name}', reason)


def get_env():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, _ = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    configuration_object = environment.get_configuration_object('configurations.yaml')
    # print(configuration_object)

    return env_name, env, configuration_object


if __name__ == '__main__':
    test_standards()
