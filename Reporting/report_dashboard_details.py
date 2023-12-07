from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


filter_by_owner = False
target_owner = 'nobody@example.com'

filter_by_id_starts_with = False
id_starts_with_list = ['00000000-dddd-bbbb-ffff']

filter_by_id_not_starts_with = False
id_not_starts_with_list = []


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []

    count_total = 0
    count_dynatrace_owned = 0

    endpoint = '/api/config/v1/dashboards'
    dashboards_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            dashboard_id = inner_dashboards_json.get('id')
            name = inner_dashboards_json.get('name')
            owner = inner_dashboards_json.get('owner')

            if not summary_mode:
                if not filter_by_owner or (filter_by_owner and target_owner in owner):
                    if not filter_by_id_starts_with or (filter_by_id_starts_with and id_starts_with_match(dashboard_id)):
                        if not filter_by_id_not_starts_with or (filter_by_id_not_starts_with and id_not_starts_with_match(dashboard_id)):
                            rows.append((name, dashboard_id, owner))

            if not filter_by_owner or (filter_by_owner and target_owner in owner):
                if not filter_by_id_starts_with or (filter_by_id_starts_with and id_starts_with_match(dashboard_id)):
                    if not filter_by_id_not_starts_with or (filter_by_id_not_starts_with and id_not_starts_with_match(dashboard_id)):
                        count_total += 1

            if not filter_by_owner and not filter_by_id_starts_with and not filter_by_id_not_starts_with and owner == 'Dynatrace':
                count_dynatrace_owned += 1

    if not summary_mode:
        print('Total Dashboards:   ' + str(count_total))
        if not filter_by_owner:
            print('Dynatrace Created:  ' + str(count_dynatrace_owned))
            summary.append('There are ' + str(count_total) + ' dashboards currently defined.  ' + str(count_dynatrace_owned) + ' were created by Dynatrace.')
        else:
            summary.append('There are ' + str(count_total) + ' dashboards currently defined owned by ' + target_owner)

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Dashboards'
        report_writer.initialize_text_file(None)
        report_headers = ('name', 'id', 'owner')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Dashboards: ' + str(count_total)])
        write_strings(['Dynatrace Created Dashboards: ' + str(count_dynatrace_owned)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def id_starts_with_match(dashboard_id):
    for id_starts_with in id_starts_with_list:
        if dashboard_id.startswith(id_starts_with):
            return True

    return False


def id_not_starts_with_match(dashboard_id):
    # Tricky due to double negation, but basically if the dashboard id is in the "must not start with" list,
    # return False as it DOES start with the string
    for id_not_starts_with in id_not_starts_with_list:
        if dashboard_id.startswith(id_not_starts_with):
            return False

    return True


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
