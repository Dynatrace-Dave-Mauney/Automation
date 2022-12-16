import math
import os
import requests
import sys
import urllib.parse

PATH = '../../$Output/Reporting/Hosts'


def get_hosts(env, token):
    # print(f'get_entity_types({env}, {token})')
    endpoint = '/api/v2/entities'
    raw_params = f'pageSize=500&entitySelector=type(HOST)&fields=+properties.monitoringMode,+properties.state,+properties.physicalMemory,+toRelationships'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    hosts = get_rest_api_json(env, token, endpoint, params)
    return hosts


def write_infra_only_candidate_hosts_file(env_name, env, token):
    output_lines = []
    # tenant_id = env.replace('https://', '').replace('.live.dynatrace.com', '')
    file_name = PATH + '/' + env_name + '_list_infra_only_candidate_hosts.html'
    with open(file_name, 'w', encoding='UTF-8') as file:
        file.write('<html>\n')
        hosts = get_hosts(env, token)
        for entities in hosts:
            total_count = int(entities.get('totalCount'))
            if total_count > 0:
                host_entities = entities.get('entities')
                for host_json in host_entities:
                    monitoring_mode = host_json.get('properties').get('monitoringMode', '')
                    state = host_json.get('properties').get('state', '')
                    if monitoring_mode == 'FULL_STACK' and state == 'RUNNING':
                        running = host_json.get('toRelationships').get('runsOnHost', [])
                        service_count = 0
                        for i in running:
                            entity_type = i['type']
                            if entity_type == 'SERVICE':
                                service_count += 1
                                break
                        if service_count == 0:
                            # Skip kubernetes nodes
                            node_of_host = host_json.get('toRelationships').get('isNodeOfHost')
                            if 'KUBERNETES_NODE' not in str(node_of_host):
                                entity_id = host_json['entityId']
                                display_name = host_json['displayName']
                                # print(f'{display_name}: {entity_id}')
                                physical_memory = host_json.get('properties').get('physicalMemory', '0')
                                physical_memory_gb = int(physical_memory) / 1000000000
                                # Host Unit Calculation:
                                # https://www.dynatrace.com/support/help/shortlink/application-and-infrastructure-host-units#host-units
                                if physical_memory_gb <= 1.6:
                                    estimated_host_units = .10
                                else:
                                    if physical_memory_gb <= 4:
                                        estimated_host_units = .25
                                    else:
                                        if physical_memory_gb <= 8:
                                            estimated_host_units = .5
                                        else:
                                            estimated_host_units = math.ceil(physical_memory_gb / 16)
                                estimated_host_units_details = f'{physical_memory} bytes => {physical_memory_gb} GB => {estimated_host_units} estimated host units'
                                print(f'{display_name} ({entity_id} {monitoring_mode} {state} {estimated_host_units_details})')
                                # html_output = '<a href="' + env + '/#newhosts/hostdetails;id=' + entity_id + '"> ' + entity_id + '</a> ' + display_name + " " + monitoring_mode + " " + state + '<br>\n'
                                # html_output = '<a href="' + env + '/#newhosts/hostdetails;id=' + display_name + '"> ' + display_name + '</a> ' + entity_id + " (" + monitoring_mode + ", " + state + ')<br>\n'
                                # html_output = display_name + '~' + '<a href="' + env + '/#newhosts/hostdetails;id=' + entity_id + '"> ' + display_name + '</a> ' + entity_id + " (" + monitoring_mode + ", " + state + ')<br>\n'
                                # html_output = display_name + '~' + '<a href="' + env + '/#newhosts/hostdetails;id=' + entity_id + '"> ' + display_name + '</a><br>\n'
                                html_output = f'{display_name}~<a href="{env}/#newhosts/hostdetails;id={entity_id}"> {display_name}</a>&nbsp({estimated_host_units_details})<br>\n'

                                # file.write(html_output)
                                output_lines.append(html_output)

        file.write(f'<h1>Candidates for infrastructure-only monitoring for {env_name}</h1>')
        for html in sorted(output_lines):
            html_line = html.split('~')[1]
            file.write(html_line)
        file.write('</html>\n')


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


def process(env_name, env, token):
    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

    print(f'Environment Name: {env_name}')
    print(f'Environment:      {env}')
    print(f'Token:            {masked_token}')

    print('')
    print('Infrastructure-Only Candidates')


    write_infra_only_candidate_hosts_file(env_name, env, token)


def run():
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env_name, env, token)


def main(arguments):
    help_text = '''
    list_infra_only_candidate_hosts.py: 
    lists hosts that are in RUNNING state with FULL_STACK enabled, but have no services

    Usage:    list_infra_only_candidate_hosts.py <tenant/environment URL> <token>
    '''

    print('args' + str(arguments))
    if len(arguments) == 1:
        run()
        exit()
    if len(arguments) < 2:
        print(help_text)
        raise ValueError('Too few arguments!')
    if len(arguments) > 4:
        print(help_text)
        raise ValueError('Too many arguments!')
    if arguments[1] in ['-h', '--help']:
        print(help_text)
    elif arguments[1] in ['-v', '--entities']:
        print('1.0')
    else:
        if len(arguments) == 4:
            env_name = arguments[1]
            env = arguments[2]
            token = arguments[3]
            process(env_name, env, token)
        else:
            print(help_text)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
