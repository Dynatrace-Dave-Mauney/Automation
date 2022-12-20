import ipaddress
import os
import requests
import socket
import ssl_expiry
import yaml
import list_urls_referenced_by_synthetics
import list_hosts_monitored_by_oneagent


# To set a default domain name and/or a list of hosts to bypass:
# configuration_yaml_file = 'check_certificates.yaml'
configuration_yaml_file = '../../$Input/Tools/Certificates/check_certificates.yaml'


def process(env, token):
    host_names = []

    total_count = 0
    skip_count = 0
    test_count = 0
    pass_count = 0
    fail_connect_count = 0
    fail_cert_count = 0

    host_names_from_synthetics = list_urls_referenced_by_synthetics.process(env, token, False)
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


def get_rest_api_json(url, token, endpoint, params):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        exit(1)

    json_data = resp.json()

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json_data) is list:
        # DEBUG:
        # print(json_data)
        return json_data

    json_list = [json_data]
    next_page_key = json_data.get('nextPageKey')

    while next_page_key is not None:
        # print(f'next_page_key: {next_page_key}')
        params = {'nextPageKey': next_page_key}
        full_url = url + endpoint
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
        # print(resp.url)

        if resp.status_code != 200:
            print('Paginated REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            exit(1)

        json_data = resp.json()
        # print(json_data)

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def get_config():
    try:
        with open(configuration_yaml_file, 'r') as file:
            document = file.read()
            return yaml.load(document, Loader=yaml.FullLoader)
    except FileNotFoundError:
        return {}


def main():
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

    print(f'Environment Name: {env_name}')
    print(f'Environment:      {env}')
    print(f'Token:            {masked_token}')

    print('')
    print('Check Certificates')

    process(env, token)


if __name__ == '__main__':
    main()
