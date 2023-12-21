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
    count_too_few_active_gates = 0
    count_default_active_gates = 0
    count_default_one_agents = 0

    endpoint = '/api/v2/networkZones'
    network_zones_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for network_zones_json in network_zones_json_list:
        inner_network_zones_json_list = network_zones_json.get('networkZones')
        for inner_network_zones_json in inner_network_zones_json_list:
            entity_id = inner_network_zones_json.get('id')
            description = inner_network_zones_json.get('description')
            alternative_zones = inner_network_zones_json.get('alternativeZones')
            # version = inner_network_zones_json.get('version')
            num_of_one_agents_using = inner_network_zones_json.get('numOfOneAgentsUsing')
            num_of_configured_one_agents = inner_network_zones_json.get('numOfConfiguredOneAgents')
            num_of_one_agents_from_other_zones = inner_network_zones_json.get('numOfOneAgentsFromOtherZones')
            num_of_configured_active_gates = inner_network_zones_json.get('numOfConfiguredActiveGates')

            if num_of_configured_active_gates < 2:
                count_too_few_active_gates += 1

            if entity_id == 'default':
                count_default_active_gates = num_of_configured_active_gates
                count_default_one_agents = num_of_one_agents_using

            alternative_zones_str = str(alternative_zones).replace('[', '')
            alternative_zones_str = alternative_zones_str.replace(']', '')
            alternative_zones_str = alternative_zones_str.replace("'", "")

            if not summary_mode:
                rows.append((entity_id, description, alternative_zones_str, str(num_of_one_agents_using), str(num_of_configured_one_agents), str(num_of_one_agents_from_other_zones), str(num_of_configured_active_gates)))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' network zones currently defined and reporting.')
    if count_too_few_active_gates > 0:
        summary.append('There are ' + str(count_too_few_active_gates) + ' network zones with less than 2 ActiveGates currently and reporting to them.')
    if count_default_active_gates > 0:
        summary.append('The default network zone has ' + str(count_default_active_gates) + ' ActiveGates reporting to it.')
    if count_default_one_agents > 0:
        summary.append('There default network zone has ' + str(count_default_one_agents) + ' OneAgents reporting to it.')

    if not summary_mode:
        report_name = 'Network Zones'
        report_writer.initialize_text_file(None)
        report_headers = ('id', 'description', 'alternativeZones', 'numOfOneAgentsUsing', 'numOfConfiguredOneAgents', 'numOfOneAgentsFromOtherZones', 'numOfConfiguredActiveGates')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Network Zones: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


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
