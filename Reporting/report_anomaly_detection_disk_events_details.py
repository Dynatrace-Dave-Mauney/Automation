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

    endpoint = '/api/config/v1/anomalyDetection/diskEvents'
    params = ''
    anomaly_json = dynatrace_api.get(env, token, endpoint, params)[0]

    anomaly_values = anomaly_json.get('values')
    for anomaly_value in anomaly_values:
        object_id = anomaly_value.get('id')
        name = anomaly_value.get('name')
        if not summary_mode:
            rows.append((name, object_id))

        count_total += 1

    summary.append('There are ' + str(count_total) + ' anomaly detection disk events currently defined.')

    if not summary_mode:
        report_name = 'Disk Event Anomaly Detection'
        report_writer.initialize_text_file(None)
        report_headers = ['Name', 'Object ID']
        report_writer.write_console(report_name, report_headers, rows, delimiter=': ')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter=': ')
        write_strings(['Total Anomaly Detection Disk Events: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def convert_boolean(boolean):
    if boolean:
        return 'on'
    else:
        return'off'
        

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
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
