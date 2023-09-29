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

    endpoint = '/api/config/v1/managementZones'
    params = ''
    management_zones_json_list = dynatrace_api.get(env, token, endpoint, params)

    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        for inner_management_zones_json in inner_management_zones_json_list:
            entity_id = inner_management_zones_json.get('id')
            name = inner_management_zones_json.get('name')
            endpoint = '/api/config/v1/managementZones/' + entity_id
            params = ''
            management_zone = dynatrace_api.get(env, token, endpoint, params)[0]
            description = management_zone.get('description')
            if not description:
                description = ''
            formatted_rules = format_rules(management_zone.get('rules'))
            formatted_dimensional_rules = format_dimensional_rules(management_zone.get('dimensionalRules'))

            # if formatted_dimensional_rules:
            #     print(f'formatted_dimensional_rules: {formatted_dimensional_rules}')

            formatted_entity_rules = format_entity_rules(management_zone.get('entitySelectorBasedRules'))

            # debug_info = f"     -------> DEBUG INFO (rules): {management_zone.get('rules')}"

            if not summary_mode:
                # rows.append((name, formatted_rules, str(debug_info)))
                rows.append((name, formatted_rules, formatted_entity_rules, formatted_dimensional_rules, entity_id, str(description)))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' management zones currently defined.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Management Zones'
        report_writer.initialize_text_file(None)
        report_headers = ('Name', 'Rules', 'Entity Rules', 'Dimensional Rules', 'ID', 'Description')
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
