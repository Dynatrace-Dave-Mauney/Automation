import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    cluster_version = get_cluster_version(env, token)
    cluster_version_split = cluster_version.split('.')
    cluster_minor_version = cluster_version_split[1]

    one_agent_auto_update_setting = get_one_agent_auto_update_setting(env, token)

    rows = []
    summary = []

    count_total = 0
    count_version_up_to_date = 0
    count_version_not_up_to_date = 0
    count_version_unsupported = 0
    max_version = 0
    min_version = 0

    endpoint = '/api/v1/oneagents'
    params = 'relativeTime=2hours'
    oneagents_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for oneagents_json in oneagents_json_list:
        inner_oneagents_json_list = oneagents_json.get('hosts')
        for inner_oneagents_json in inner_oneagents_json_list:

            # import json
            # formatted_json = json.dumps(inner_oneagents_json, indent=4, sort_keys=False)
            # print(formatted_json)

            host_info = inner_oneagents_json.get('hostInfo')
            entity_id = host_info.get('entityId')
            display_name = host_info.get('displayName')
            discovered_name = host_info.get('discoveredName')
            consumed_host_units = host_info.get('consumedHostUnits')

            version_status = 'N/A'
            agent_major_version = 0
            agent_minor_version = 0
            agent_revision_version = 0
            agent_version = host_info.get('agentVersion')
            if agent_version:
                agent_major_version = agent_version.get('major')
                agent_minor_version = agent_version.get('minor')
                agent_revision_version = agent_version.get('revision')
                # print(agent_version, agent_minor_version, display_name)
                if int(agent_minor_version) < int(cluster_minor_version) - 2:
                    version_status = 'Not Up To Date'
                    count_version_not_up_to_date += 1
                    if int(agent_minor_version) < int(cluster_minor_version) - 24:
                        version_status = 'Unsupported'
                        count_version_unsupported += 1
                else:
                    version_status = 'Up To Date'
                    count_version_up_to_date += 1

            if agent_version:
                if int(agent_minor_version) > max_version:
                    max_version = int(agent_minor_version)

                if int(agent_minor_version) < min_version or min_version == 0:
                    min_version = int(agent_minor_version)

                version = f'{agent_major_version}.{agent_minor_version}.{agent_revision_version}'
            else:
                version = 'N/A'

            if not summary_mode:
                rows.append((display_name, discovered_name, entity_id, version, version_status, consumed_host_units))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' OneAgents.')
    summary.append('There are ' + str(count_version_up_to_date) + ' OneAgents with up to date versions.')
    summary.append('There are ' + str(count_version_not_up_to_date) + ' OneAgents with not up to date versions.')
    summary.append('There are ' + str(count_version_unsupported) + ' OneAgents with unsupported versions.')
    summary.append('The newest OneAgent version is ' + str(max_version))
    summary.append('The oldest OneAgent version is ' + str(min_version))
    summary.append('OneAgent automatic update setting is ' + str(one_agent_auto_update_setting))

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'OneAgents'
        report_writer.initialize_text_file(None)
        report_headers = ('displayName', 'discoveredName', 'entityId', 'version', 'version status', 'consumedHostUnits')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total OneAgents: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def get_cluster_version(env, token):
    endpoint = '/api/v1/config/clusterversion'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    entities_json = r.json()
    version = entities_json.get('version')
    return version


def get_one_agent_auto_update_setting(env, token):
    endpoint = '/api/v2/settings/objects'
    schema_ids = 'builtin:deployment.oneagent.updates'
    schema_ids_param = f'schemaIds={schema_ids}'
    raw_params = schema_ids_param + '&scopes=environment&fields=schemaId,value,Summary'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token, params=params)
    # one_agent_auto_update_setting = r.json()
    one_agent_auto_update_setting = r.json().get('items')[0].get('value').get('updateMode')
    return one_agent_auto_update_setting


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
