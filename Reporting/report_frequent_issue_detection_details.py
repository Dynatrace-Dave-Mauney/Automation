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

    endpoint = '/api/config/v1/frequentIssueDetection'
    params = ''
    frequent_issue_detection_json = dynatrace_api.get(env, token, endpoint, params)[0]

    frequent_issue_detection_application_enabled = frequent_issue_detection_json.get('frequentIssueDetectionApplicationEnabled')
    frequent_issue_detection_service_enabled = frequent_issue_detection_json.get('frequentIssueDetectionServiceEnabled')
    frequent_issue_detection_infrastructure_enabled = frequent_issue_detection_json.get('frequentIssueDetectionInfrastructureEnabled')

    if not summary_mode:
        rows.append((str(frequent_issue_detection_application_enabled), str(frequent_issue_detection_service_enabled), str(frequent_issue_detection_infrastructure_enabled)))

    if frequent_issue_detection_application_enabled and frequent_issue_detection_service_enabled and frequent_issue_detection_infrastructure_enabled:
        summary.append('Frequent issue detection is turned on for applications, services and infrastructure.  This is the default setting.')
    else:
        if frequent_issue_detection_application_enabled:
            application_setting = 'on'
        else:
            application_setting = 'off'
        if frequent_issue_detection_service_enabled:
            service_setting = 'on'
        else:
            service_setting = 'off'
        if frequent_issue_detection_infrastructure_enabled:
            infrastructure_setting = 'on'
        else:
            infrastructure_setting = 'off'
        summary.append('Frequent issue detection is turned ' + application_setting + ' for applications, ' + service_setting + ' for services and ' + infrastructure_setting + ' for infrastructure.')

    if not summary_mode:
        report_name = 'Frequent Issue Detection'
        report_writer.initialize_text_file(None)
        report_headers = ('frequentIssueDetectionApplicationEnabled', 'frequentIssueDetectionServiceEnabled', 'frequentIssueDetectionInfrastructureEnabled')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
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
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
