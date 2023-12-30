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
    count_key_value = 0
    count_key_only = 0

    endpoint = '/api/config/v1/autoTags'
    auto_tags_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for auto_tags_json in auto_tags_json_list:
        inner_auto_tags_json_list = auto_tags_json.get('values')
        for inner_auto_tags_json in inner_auto_tags_json_list:
            entity_id = inner_auto_tags_json.get('id')
            name = inner_auto_tags_json.get('name')

            endpoint = '/api/config/v1/autoTags/' + entity_id
            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
            auto_tag = r.json()

            # import json
            # formatted_auto_tag = json.dumps(auto_tag, indent=4, sort_keys=False)
            # print(formatted_auto_tag)

            key_value_string = ''
            rules = auto_tag.get('rules')
            if is_key_value(rules):
                key_value_string = 'Key/Value Pair'
                count_key_value += 1
            else:
                key_value_string = 'Key Only'
                count_key_only += 1

            if not summary_mode:
                rows.append((name, entity_id, key_value_string, str(rules)))

            count_total += 1

    rows = sorted(rows)

    summary.append(f'There are {count_total} automatically applied tags currently defined.')
    summary.append(f'There are {count_key_value} key/value automatically applied tags currently defined.')
    summary.append(f'There are {count_key_only} key only automatically applied tags currently defined.')

    if not summary_mode:
        report_name = 'Automatic Tags'
        report_writer.initialize_text_file(None)
        report_headers = ('Name', 'ID', 'Key/Value Finding', 'Rules')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_string(f'Total Automatically Applied Tags: {count_total}')
        write_string(f'Total Automatically Applied Key/Value Tags: {count_key_value}')
        write_string(f'Total Automatically Applied Key Only Tags: {count_key_only}')
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_string(string):
    report_writer.write_console_plain_text([string])
    report_writer.write_plain_text(None, [string])


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def is_key_value(rules):
    for rule in rules:
        value_format = rule.get('valueFormat')
        if value_format:
            return True

    return False


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
