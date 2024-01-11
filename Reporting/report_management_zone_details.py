from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer
from Reuse import standards

perform_check_naming_standard = False
report_naming_standard_violations_only = False


def summarize(env, token, **kwargs):
    global perform_check_naming_standard
    if kwargs:
        perform_check_naming_standard = kwargs.get('perform_check_naming_standard', False)
    return process_report(env, token, True, **kwargs)


def process(env, token, **kwargs):
    global perform_check_naming_standard
    global report_naming_standard_violations_only
    if kwargs:
        perform_check_naming_standard = kwargs.get('perform_check_naming_standard', False)
        report_naming_standard_violations_only = kwargs.get('report_naming_standard_violations_only', False)
    return process_report(env, token, False, **kwargs)


def process_report(env, token, summary_mode, **kwargs):
    rows = []
    summary = []

    count_total = 0
    count_naming_standard_pass = 0
    count_naming_standard_fail = 0

    endpoint = '/api/config/v1/managementZones'
    management_zones_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        for inner_management_zones_json in inner_management_zones_json_list:
            entity_id = inner_management_zones_json.get('id')
            name = inner_management_zones_json.get('name')

            # if '-PRD' not in name.upper():
            #     continue

            endpoint = '/api/config/v1/managementZones'
            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            management_zone = r.json()

            description = management_zone.get('description', '')
            formatted_rules = format_rules(management_zone.get('rules'))
            formatted_dimensional_rules = format_dimensional_rules(management_zone.get('dimensionalRules'))

            # if formatted_dimensional_rules:
            #     print(f'formatted_dimensional_rules: {formatted_dimensional_rules}')

            formatted_entity_rules = format_entity_rules(management_zone.get('entitySelectorBasedRules'))

            # debug_info = f"     -------> DEBUG INFO (rules): {management_zone.get('rules')}"

            standard_string = 'N/A'
            standard_met = True
            if perform_check_naming_standard:
                standard_met, reason = check_naming_standard(name, **kwargs)
                if standard_met:
                    standard_string = 'Meets naming standards'
                    count_naming_standard_pass += 1
                else:
                    standard_string = f'Does not meet naming standards because {reason}'
                    # print(name, standard_string)
                    count_naming_standard_fail += 1

            if not summary_mode:
                # rows.append((name, formatted_rules, formatted_entity_rules, formatted_dimensional_rules, entity_id, description))
                if not report_naming_standard_violations_only or (report_naming_standard_violations_only and not standard_met):
                    rows.append((name, formatted_rules, formatted_entity_rules, formatted_dimensional_rules, entity_id, description, standard_string))

            count_total += 1

    summary.append(f'There are {count_total} management zones currently defined.')

    if perform_check_naming_standard:
        summary.append(f'There are {count_naming_standard_pass} management zones currently defined that meet the naming standard.')
        summary.append(f'There are {count_naming_standard_fail} management zones currently defined that do not meet the naming standard.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Management Zones'
        report_writer.initialize_text_file(None)
        report_headers = ('Name', 'Rules', 'Entity Rules', 'Dimensional Rules', 'ID', 'Description', 'Naming Standard Finding')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Management Zones: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def format_rules(rules):
    formatted_rules = []
    for rule in rules:
        rule_type = rule.get('type')
        enabled = f"({rule.get('enabled')})"
        if enabled:
            enabled = ''
        else:
            enabled = ' (Disabled)'

        propagation_types = rule.get('propagationTypes')
        formatted_propagation_types = format_propagation_types(propagation_types)

        conditions = rule.get('conditions')
        formatted_conditions = format_conditions(conditions)

        formatted_rules.append(f'{rule_type} Rule{enabled}: {str(formatted_conditions)}{formatted_propagation_types}')

    # Improve readability if list size is one
    if len(formatted_rules) == 1:
        formatted_rules = formatted_rules[0]

    return str(formatted_rules)


def format_conditions(conditions):
    case_sensitive_string = ''
    formatted_conditions = []
    for condition in conditions:
        condition_string = ''
        condition_key = condition.get('key')
        if condition_key:
            condition_key_attribute = condition_key.get('attribute')
            if condition_key_attribute:
                condition_string += condition_key_attribute

        condition_comparison_info = condition.get('comparisonInfo')
        if condition_comparison_info:
            condition_comparison_info_type = condition_comparison_info.get('type')
            condition_comparison_info_operator = condition_comparison_info.get('operator')
            condition_comparison_info_negate = condition_comparison_info.get('negate')
            if condition_comparison_info_negate:
                negate_string = 'not '
            else:
                negate_string = ''
            condition_comparison_info_case_sensitive = condition_comparison_info.get('caseSensitive')
            if condition_comparison_info_case_sensitive is None:
                case_sensitive_string = ''
            else:
                if condition_comparison_info_case_sensitive:
                    case_sensitive_string = ' (case sensitive)'
                else:
                    case_sensitive_string = ' (case insensitive)'
            condition_comparison_info_value = condition_comparison_info.get('value')
            if condition_comparison_info_value:
                if isinstance(condition_comparison_info_value, dict):
                    condition_comparison_info_value_key = condition_comparison_info_value.get('key')
                    condition_comparison_info_value_value = condition_comparison_info_value.get('value')
                    if condition_comparison_info_type and condition_comparison_info_operator and condition_comparison_info_value_key and condition_comparison_info_value_value:
                        condition_string += f' {condition_comparison_info_type.lower()} {condition_comparison_info_value_key} {negate_string}{condition_comparison_info_operator.lower()} {condition_comparison_info_value_value}'
                else:
                    condition_string += f' {condition_comparison_info_type.lower()} {negate_string}{condition_comparison_info_operator.lower()} {condition_comparison_info_value}'
            else:
                condition_string += f' {condition_comparison_info_type.lower()} {negate_string}{condition_comparison_info_operator.lower()}'
        else:
            condition_string = ' no comparison info '

        condition_string += case_sensitive_string

        # print(f'condition_string: {condition_string} condition: {condition}')

        formatted_conditions.append(condition_string)

    # Improve readability if list size is one
    if len(formatted_conditions) == 1:
        formatted_conditions = formatted_conditions[0]

    return str(formatted_conditions)


def format_propagation_types(propagation_types):
    if not propagation_types:
        return ''

    formatted_propagation_types = []
    propagation_type_readable_list = []
    for propagation_type in propagation_types:
        import re
        propagation_type_readable = re.sub('.*_TO_', '', propagation_type).lower()
        propagation_type_readable_list.append(propagation_type_readable)

    propagation_type_readable_list_string = report_writer.stringify_list(propagation_type_readable_list)
    propagation_type_readable_list_string = propagation_type_readable_list_string.replace('_like', '')
    propagation_type_readable_list_string = propagation_type_readable_list_string.replace('_', ' ')
    propagation_type_string = f' (with propagation to {str(propagation_type_readable_list_string)})'
    formatted_propagation_types.append(propagation_type_string)

    # Improve readability if list size is one
    if len(formatted_propagation_types) == 1:
        formatted_propagation_types = formatted_propagation_types[0]

    return str(formatted_propagation_types)


def format_entity_rules(entity_rules):
    if not entity_rules:
        return ''

    formatted_entity_rules = []
    for entity_rule in entity_rules:
        enabled = entity_rule.get('enabled')
        if enabled is None or enabled:
            enabled = ''
        else:
            enabled = ' (Disabled)'
        entity_selector = entity_rule.get('entitySelector')
        if entity_selector:
            formatted_entity_rules.append(f'{entity_selector}{enabled}')
        else:
            formatted_entity_rules.append(str(entity_rule))

    # Improve readability if list size is one
    if len(formatted_entity_rules) == 1:
        formatted_entity_rules = formatted_entity_rules[0]

    return str(formatted_entity_rules)


def format_dimensional_rules(dimensional_rules):
    if not dimensional_rules:
        return ''

    formatted_dimensional_rules = []
    for dimensional_rule in dimensional_rules:
        enabled = dimensional_rule.get('enabled')
        if enabled is None or enabled:
            enabled = ''
        else:
            enabled = ' (Disabled)'
        dimensional_selector = dimensional_rule.get('dimensionalSelector')
        if dimensional_selector:
            formatted_dimensional_rules.append(f'{dimensional_selector}{enabled}')
        else:
            formatted_dimensional_rules.append(str(dimensional_rule))

    # Improve readability if list size is one
    if len(formatted_dimensional_rules) == 1:
        formatted_dimensional_rules = formatted_dimensional_rules[0]

    return str(formatted_dimensional_rules)


def check_naming_standard(name, **kwargs):
    env_name = kwargs.get('env_name')
    if not env_name:
        return False, 'Environment name ("env_name") must be passed'

    configuration_object = environment.get_configuration_object('configurations.yaml')

    if not configuration_object:
        return False, 'Configuration object ("configuration_object") could not be loaded'

    return standards.check_naming_standard(env_name, name, configuration_object, 'management zone')


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
    # process(env, token)
    # process(env, token, env_name=env_name_supplied, perform_check_naming_standard=True)
    print(summarize(env, token, env_name=env_name_supplied, perform_check_naming_standard=True))

    
if __name__ == '__main__':
    main()
