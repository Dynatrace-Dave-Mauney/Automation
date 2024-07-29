"""
Download dashboards from the tenant to the path indicated below.
"""

from Reuse import download_entity
from Reuse import environment


download_path = 'downloads'
entity_type = 'dashboards'
endpoint = '/api/config/v1/dashboards'


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Upper'
    # env_name_supplied = 'Lower'
    # env_name_supplied = 'Sandbox'
    #
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    download_entity.download(env_name, env, token, entity_type, endpoint, download_path, values_key='dashboards')


if __name__ == '__main__':
    main()
