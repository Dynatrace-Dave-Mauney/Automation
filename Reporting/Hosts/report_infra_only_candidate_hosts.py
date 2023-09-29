import math
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    process_report(env, token)


def process_report(env, token):
    rows = []
    count_total = 0
    total_estimated_host_units = 0

    endpoint = '/api/v2/entities'
    raw_params = f'pageSize=500&entitySelector=type(HOST)&fields=+properties.monitoringMode,+properties.state,+properties.physicalMemory,+toRelationships'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    hosts = dynatrace_api.get(env, token, endpoint, params)

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
                            count_total += 1
                            total_estimated_host_units += estimated_host_units
                            rows.append((display_name, entity_id, monitoring_mode, state, physical_memory, physical_memory_gb, estimated_host_units))

    rows.append(('Total', '', '', '', '', '', total_estimated_host_units))

    report_name = 'Infrastructure-Only Candidates'
    report_writer.initialize_text_file(None)
    report_headers = ('Display Name', 'ID', 'Monitoring Mode', 'State', 'Memory (Bytes)', 'Memory (GB)', 'Estimated Host Units')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)


if __name__ == '__main__':
    main()
