import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

perform_check_naming_standard = False
report_naming_standard_violations_only = False


def summarize(env, token, **kwargs):
    global perform_check_naming_standard
    perform_check_naming_standard = kwargs.get('perform_check_naming_standard', False)
    return process_report(env, token, True)


def process(env, token, **kwargs):
    global perform_check_naming_standard
    global report_naming_standard_violations_only
    perform_check_naming_standard = kwargs.get('perform_check_naming_standard', False)
    report_naming_standard_violations_only = kwargs.get('report_naming_standard_violations_only', False)
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []

    count_total = 0
    count_total_hosts_in_groups = 0
    count_total_host_groups_without_hosts = 0
    count_naming_standard_pass = 0
    count_naming_standard_fail = 0

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST_GROUP)&fields=+properties,+toRelationships&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')

            # if '-PRD' not in display_name.upper():
            #     continue

            properties = inner_entities_json.get('properties')
            detected_name = properties.get('detectedName', '')
            to_relationships = inner_entities_json.get('toRelationships')
            if to_relationships:
                hosts_in_group = len(to_relationships.get('isInstanceOf', []))
            else:
                hosts_in_group = 0

            hosts_in_group_str = str(hosts_in_group)

            standard_string = 'N/A'
            standard_met = True
            if perform_check_naming_standard:
                standard_met, reason = check_naming_standard(env, display_name)
                if standard_met:
                    standard_string = 'Meets naming standards'
                    count_naming_standard_pass += 1
                else:
                    standard_string = f'Does not meet naming standards because {reason}'
                    count_naming_standard_fail += 1

            if not summary_mode:
                if not report_naming_standard_violations_only or (report_naming_standard_violations_only and not standard_met):
                    rows.append((display_name, entity_id, detected_name, hosts_in_group_str, standard_string))

            count_total += 1
            count_total_hosts_in_groups = count_total_hosts_in_groups + hosts_in_group
            if hosts_in_group == 0:
                count_total_host_groups_without_hosts += 1

    rows = sorted(rows)

    summary.append('There are ' + str(count_total) + ' hosts groups currently defined.  ')
    if count_total > 0:
        summary.append(f'{count_total_hosts_in_groups} hosts currently belong to a host group.')
        summary.append(f'{count_total_host_groups_without_hosts} host groups contain no hosts.')
        if perform_check_naming_standard:
            summary.append(f'There are {count_naming_standard_pass} hosts groups currently defined that meet the naming standard.')
            summary.append(f'There are {count_naming_standard_fail} hosts groups currently defined that do not meet the naming standard.')

    if not summary_mode:
        report_name = 'Host Groups'
        report_writer.initialize_text_file(None)
        report_headers = ('displayName', 'entityId', 'detectedName', 'Hosts In Group', 'Naming Standard Finding')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Host Groups: ' + str(count_total)])
        write_strings(['Total Hosts in Host Groups: ' + str(count_total_hosts_in_groups)])
        write_strings(['Total Host Groups With No Hosts: ' + str(count_total_host_groups_without_hosts)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def check_naming_standard(env, name):
    name_split_list = name.split('-')
    name_hyphen_count = len(name_split_list) - 1
    if name_hyphen_count == 0 or name_hyphen_count > 2:
        print('Rule 1', name, name_hyphen_count, name_split_list)
        return False, 'Name must have one or two hyphens'
    else:
        if env.startswith('https://p'):
            if name_split_list[1].upper() not in ['PROD', 'DR']:
                print('Rule 2', name, name_hyphen_count, name_split_list)
                return False, 'Production name must end with "-PROD" or "-DR"'
        else:
            if name_split_list[1].upper() not in ['DEV', 'SIT', 'UAT', 'QA', 'STG', 'IAT', 'SAND', 'TEST', 'NPRD', 'RST', 'GW', 'STG1', 'STG2', 'STG3', 'UAT1', 'UAT2', 'UAT3', 'DEV1', 'DEV2', 'DEV3']:
                print('Rule 3', name, name_hyphen_count, name_split_list)
                return False, 'Non-Production name must end with "-DEV", "-SIT", etc.'

    # print('Rule 4', name, name_hyphen_count, name_split_list)
    return True, 'Name meets standards'


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    # process(env, token)
    process(env, token, perform_check_naming_standard=True, report_naming_standard_violations_only=True)

    
if __name__ == '__main__':
    main()
