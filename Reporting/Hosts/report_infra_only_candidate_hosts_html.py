import math
import sys
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


PATH = '../../$Output/Reporting/Hosts'


def get_hosts(env, token):
    # print(f'get_entity_types({env}, {token})')
    endpoint = '/api/v2/entities'
    raw_params = f'pageSize=500&entitySelector=type(HOST)&fields=+properties.monitoringMode,+properties.state,+properties.physicalMemory,+toRelationships'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    hosts = dynatrace_api.get(env, token, endpoint, params)
    return hosts


def write_infra_only_candidate_hosts_file(env_name, env, token):
    output_lines = []
    total_hosts = 0
    total_estimated_host_units = 0
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
                                total_hosts += 1
                                total_estimated_host_units += estimated_host_units
                                estimated_host_units_details = f'{physical_memory} bytes => {physical_memory_gb} GB => {estimated_host_units} estimated host units'
                                print(f'{display_name} ({entity_id} {monitoring_mode} {state} {estimated_host_units_details})')
                                # html_output = '<a href="' + env + '/#newhosts/hostdetails;id=' + entity_id + '"> ' + entity_id + '</a> ' + display_name + " " + monitoring_mode + " " + state + '<br>\n'
                                # html_output = '<a href="' + env + '/#newhosts/hostdetails;id=' + display_name + '"> ' + display_name + '</a> ' + entity_id + " (" + monitoring_mode + ", " + state + ')<br>\n'
                                # html_output = display_name + '~' + '<a href="' + env + '/#newhosts/hostdetails;id=' + entity_id + '"> ' + display_name + '</a> ' + entity_id + " (" + monitoring_mode + ", " + state + ')<br>\n'
                                # html_output = display_name + '~' + '<a href="' + env + '/#newhosts/hostdetails;id=' + entity_id + '"> ' + display_name + '</a><br>\n'
                                html_output = f'{display_name}~<a href="{env}/#newhosts/hostdetails;id={entity_id}"> {display_name}</a>&nbsp({estimated_host_units_details})<br>\n'

                                # file.write(html_output)
                                output_lines.append(html_output)

        print('')
        print(f'Total estimated host units that could be saved by switching {total_hosts} to infrastructure-only mode: {total_estimated_host_units} ')
        print('')

        file.write(f'<h1>Candidates for infrastructure-only monitoring for {env_name}</h1>')
        for html in sorted(output_lines):
            html_line = html.split('~')[1]
            file.write(html_line)
        file.write('</html>\n')


def process(env_name, env, token):
    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

    print(f'Environment Name: {env_name}')
    print(f'Environment:      {env}')
    print(f'Token:            {masked_token}')

    print('')
    print('Infrastructure-Only Candidates')


    write_infra_only_candidate_hosts_file(env_name, env, token)


def run():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

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
