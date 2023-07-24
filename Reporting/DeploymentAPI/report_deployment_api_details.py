from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    process_connectivity_info(env, token)
    process_versions(env, token)
    process_latest_version(env, token)
    process_active_gate_endpoints(env, token)


def process_connectivity_info(env, token):
    print('Connectivity Info:')
    endpoint = '/api/v1/deployment/installer/agent/connectioninfo'
    params = ''
    connectivity_info_json_list = dynatrace_api.get(env, token, endpoint, params)

    for connectivity_info_json in connectivity_info_json_list:
        tenant_uuid = connectivity_info_json.get('tenantUUID')
        tenant_token = connectivity_info_json.get('tenantToken')
        print(f'Tenant UUID: {tenant_uuid}')
        print(f'Tenant Token: {tenant_token}')

        communication_endpoints = connectivity_info_json.get('communicationEndpoints')

        for communication_endpoint in communication_endpoints:
            print(communication_endpoint)


def process_active_gate_endpoints(env, token):
    endpoint = '/api/v1/deployment/installer/agent/connectioninfo/endpoints'
    active_gate_endpoints = dynatrace_api.get_plain_text_list(env, token, endpoint)
    print('ActiveGate Endpoints:')
    print(active_gate_endpoints)


def process_versions(env, token):
    print('Available OneAgent Versions:')
    os_type_list = ['windows', 'unix', 'aix', 'solaris', 'zos']
    installer_type_list = ['default', 'default-unattended', 'mainframe', 'paas', 'paas-sh']

    for os_type in os_type_list:
        for installer_type in installer_type_list:
            endpoint = f'/api/v1/deployment/installer/agent/versions/{os_type}/{installer_type}'
            params = ''
            agent_version_json_list = dynatrace_api.get(env, token, endpoint, params)
            for agent_version_json in agent_version_json_list:
                available_versions = agent_version_json.get('availableVersions')
                if available_versions:
                    print(f'OS Type: {os_type}')
                    print(f'Installer Type: {installer_type}')
                    print('Available Versions')
                    for available_version in available_versions:
                        print(available_version)


def process_latest_version(env, token):
    print('Latest OneAgent Versions:')
    os_type_list = ['windows', 'unix', 'aix', 'solaris', 'zos']
    installer_type_list = ['default', 'default-unattended', 'mainframe', 'paas', 'paas-sh']

    for os_type in os_type_list:
        for installer_type in installer_type_list:
            endpoint = f'/api/v1/deployment/installer/agent/{os_type}/{installer_type}/latest/metainfo'
            params = ''
            agent_version_json_list = dynatrace_api.get(env, token, endpoint, params)
            for agent_version_json in agent_version_json_list:
                latest_version = agent_version_json.get('latestAgentVersion')
                if latest_version:
                    print(f'Latest Agent Version for OS Type: {os_type} and Installer Type: {installer_type}: {latest_version}')


def main():
    friendly_function_name = 'Dynatrace Automation Reporting Deployment'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
