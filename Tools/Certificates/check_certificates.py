import ipaddress
import socket
import ssl_expiry
import yaml
import list_hosts_referenced_by_synthetics
import list_hosts_monitored_by_oneagent

from Reuse import environment


# To set a default domain name and/or a list of hosts to bypass:
configuration_yaml_file = 'check_certificates.yaml'
# configuration_yaml_file = '../../$Input/Tools/Certificates/check_certificates.yaml'
# configuration_yaml_file = '../../$Input/Tools/Certificates/check_certificates_customer_specific.yaml'


def process(env, token):
    host_names = []

    total_count = 0
    skip_count = 0
    test_count = 0
    pass_count = 0
    fail_connect_count = 0
    fail_cert_count = 0

    host_names_from_synthetics = list_hosts_referenced_by_synthetics.process(env, token, False)
    host_name_from_oneagents = list_hosts_monitored_by_oneagent.process(env, token, False)

    host_names.extend(host_names_from_synthetics)
    host_names.extend(host_name_from_oneagents)

    host_name_list = remove_duplicates(sorted(host_names))

    config = get_config()

    default_domain_name = config.get('default_domain_name', 'example.com')
    host_names_to_exclude = config.get('host_names_to_exclude', [])

    print(f'Default Domain Name:    {default_domain_name}')
    print(f'Host Exclude List Size: {len(host_names_to_exclude)}')

    for host_name in host_name_list:
        if '.' in host_name:
            pass
        else:
            if host_name != '' and not host_name.startswith('ip-'):
                # print(f'Added domain to {host_name}')
                host_name += '.' + default_domain_name

        total_count += 1

        if host_name in host_names_to_exclude:
            skip_count += 1
            # print(f'Skipping {host_name}...')
            continue

        test_count += 1
        try:
            # print(f'Checking: "{host_name}"')
            message = ssl_expiry.test_host(host_name)
            # print(message)
            if 'is fine' in message:
                pass_count += 1
            else:
                if 'cert error' in message:
                    fail_cert_count += 1
                    print(message)
                else:
                    fail_connect_count += 1
        except socket.gaierror:
            # print(f'{host_name} socket get address information error')
            fail_connect_count += 1
        except ConnectionRefusedError:
            # print(f'{host_name} No connection could be made because the target machine actively refused it')
            fail_connect_count += 1

    pass_rate = round((pass_count / test_count) * 100, 2)
    fail_count = fail_connect_count + fail_cert_count
    failure_rate = round((fail_count / test_count) * 100, 2)
    failure_rate_connect = round((fail_connect_count / test_count) * 100, 2)
    failure_rate_cert = round((fail_cert_count / test_count) * 100, 2)
    coverage_rate = round((test_count / total_count) * 100, 2)

    print(f'Hosts:                         {total_count}')
    print(f'Hosts Skipped:                 {skip_count}')
    print(f'Hosts Tested:                  {test_count}')
    print(f'Coverage Rate:                 {coverage_rate}')
    print(f'Hosts Passed:                  {pass_count}')
    print(f'Hosts Failed:                  {fail_count}')
    print(f'Success Rate:                  {pass_rate}')
    print(f'Failure Rate:                  {failure_rate}')
    print(f'Hosts Certificate Failed:      {fail_cert_count}')
    print(f'Failure Rate for Certificates: {failure_rate_cert}')
    print(f'Hosts Connection Failed:       {fail_connect_count}')
    print(f'Failure Rate for Connections:  {failure_rate_connect}')


def valid_ip_address(host_name):
    try:
        ipaddress.ip_address(host_name)
        return True
    except ValueError:
        return False


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


def get_tag_value(key, tags, default_value):
    text_to_check = f"'key': '{key}'"
    if text_to_check in str(tags):
        for tag in tags:
            if text_to_check in str(tag):
                return tag.get('value')
    return default_value


def get_config():
    try:
        with open(configuration_yaml_file, 'r') as file:
            document = file.read()
            return yaml.load(document, Loader=yaml.FullLoader)
    except FileNotFoundError:
        return {}


def main():
    friendly_function_name = 'Dynatrace Automation Tools'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    print('Check Certificates')

    process(env, token)


if __name__ == '__main__':
    main()
