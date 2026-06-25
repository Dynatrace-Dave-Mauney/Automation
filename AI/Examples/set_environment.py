from Reuse import environment

def set_environment():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)

    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Int'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'

    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)


if __name__ == '__main__':
    set_environment()
