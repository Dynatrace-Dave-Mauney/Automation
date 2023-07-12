from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    endpoint = '/api/config/v1/frequentIssueDetection'
    params = ''
    frequent_issue_detection_json = dynatrace_api.get(env, token, endpoint, params)[0]

    if print_mode:
        print('frequentIssueDetectionApplicationEnabled' + '|' + 'frequentIssueDetectionServiceEnabled' + '|' + 'frequentIssueDetectionInfrastructureEnabled')

    frequent_issue_detection_application_enabled = frequent_issue_detection_json.get('frequentIssueDetectionApplicationEnabled')
    frequent_issue_detection_service_enabled = frequent_issue_detection_json.get('frequentIssueDetectionServiceEnabled')
    frequent_issue_detection_infrastructure_enabled = frequent_issue_detection_json.get('frequentIssueDetectionInfrastructureEnabled')

    # TESTING
    # frequent_issue_detection_application_enabled = True
    # frequent_issue_detection_service_enabled = False
    # frequent_issue_detection_infrastructure_enabled = True

    if print_mode:
        print(str(frequent_issue_detection_application_enabled) + '|' + str(frequent_issue_detection_service_enabled) + '|' + str(frequent_issue_detection_infrastructure_enabled))

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

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)
        

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
    process(env, token, True)
    
    
if __name__ == '__main__':
    main()
