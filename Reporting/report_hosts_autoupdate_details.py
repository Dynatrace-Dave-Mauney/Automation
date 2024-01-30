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

    endpoint = '/api/config/v1/hosts/autoupdate'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    hosts_autoupdate_json = r.json()

    setting = hosts_autoupdate_json.get('setting')
    version = hosts_autoupdate_json.get('version')
    update_windows = hosts_autoupdate_json.get('updateWindows').get("windows")

    if not summary_mode:
        rows.append((str(setting), str(version), str(update_windows)))

    if setting == 'ENABLED' and version is None and update_windows == []:
        summary.append('OneAgent Auto Update is turned on.  This is not recommended for Production environments.  Consider doing manual updates or using OneAgent Maintenance Windows.')
    else:
        summary.append('OneAgent Auto Update settings have been modified as follows.' + '\r\n' +
                       'Setting is ' + setting + ', version is ' + str(version) + ' and update windows are ' + str(update_windows) + '.')

    if not summary_mode:
        report_name = 'OneAgent Auto Update Settings'
        report_writer.initialize_text_file(None)
        report_headers = ('setting', 'version', 'updateWindows')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def convert_boolean(boolean):
    if boolean:
        return 'on'
    else:
        return'off'


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
