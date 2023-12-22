import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []

    count_total = 0
    count_has_host_group = 0
    count_has_no_host_group = 0
    count_has_no_host_group_but_should_probably = 0

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            properties = inner_entities_json.get('properties')
            monitoring_mode = properties.get('monitoringMode', '')
            logical_cpu_cores = str(properties.get('logicalCpuCores', ''))
            cpu_cores = str(properties.get('cpuCores', ''))
            memory_total = str(properties.get('memoryTotal', ''))
            os_type = properties.get('osType', '')
            state = properties.get('state', 'NONE')
            network_zone = properties.get('networkZone', 'NONE')
            hypervisor_type = properties.get('hypervisorType', 'NONE')
            paas_vendor_type = properties.get('paasVendorType', 'NONE')
            cloud_type = properties.get('cloudType', 'On Premise')
            tags = inner_entities_json.get('tags', [])
            k8s_cluster = ''
            environment_name = ''
            data_center = ''
            for tag in tags:
                if "Kubernetes Cluster" in str(tag):
                    k8s_cluster = tag.get('value', '')
                if "Environment" in str(tag):
                    environment_name = tag.get('value', '')
                if "Data Center" in str(tag) or "Datacenter" in str(tag):
                    data_center = tag.get('value', '')

            host_group_name = properties.get('hostGroupName', None)
            if host_group_name:
                count_has_host_group += 1
            else:
                count_has_no_host_group += 1
                if paas_vendor_type != 'AZURE_WEBSITES' and paas_vendor_type != 'AWS_ECS_FARGATE':
                    count_has_no_host_group_but_should_probably += 1

            if not summary_mode:
                if not host_group_name:
                    rows.append((display_name, entity_id, monitoring_mode, paas_vendor_type, logical_cpu_cores, cpu_cores, memory_total, os_type, state, network_zone, hypervisor_type, cloud_type, k8s_cluster, environment_name, data_center))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' hosts currently being monitored.  ')
    if count_total > 0:
        summary.append(
            str(count_has_host_group) + ' hosts have a host group.  ' +
            str(count_has_no_host_group) + ' hosts do not have a host group.  ' +
            str(count_has_no_host_group_but_should_probably) + ' hosts do not have a host group and probably should.  ')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Hosts Without A Host Group'
        report_writer.initialize_text_file(None)
        report_headers = ('displayName', 'entityId', 'monitoringMode', 'paasVendorType', 'logicalCpuCores', 'cpuCores', 'memoryTotal', 'osType', 'state', 'networkZone', 'hypervisorType', 'cloudType', 'k8sCluster', 'environment', 'dataCenter')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Hosts: ' + str(count_total)])
        write_strings(['Hosts with Host Groups: ' + str(count_has_host_group)])
        write_strings(['Hosts without Host Groups: ' + str(count_has_no_host_group)])
        write_strings(['Hosts without Host Groups (and probably should have one): ' + str(count_has_no_host_group_but_should_probably)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def sort_and_stringify_dictionary_items(any_dict):
    dict_str = str(sorted(any_dict.items()))
    dict_str = dict_str.replace('[', '')
    dict_str = dict_str.replace(']', '')
    dict_str = dict_str.replace('), (', '~COMMA~')
    dict_str = dict_str.replace('(', '')
    dict_str = dict_str.replace(')', '')
    dict_str = dict_str.replace(',', ':')
    dict_str = dict_str.replace('~COMMA~', ', ')
    dict_str = dict_str.replace("'", "")
    return dict_str


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
    # print(summarize(env, token))


if __name__ == '__main__':
    main()
