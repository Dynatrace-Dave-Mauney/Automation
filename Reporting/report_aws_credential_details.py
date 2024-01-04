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

    endpoint = '/api/config/v1/aws/credentials'
    aws_credentials_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for aws_credentials_json in aws_credentials_json_list:
        entity_id = aws_credentials_json.get('id')
        name = aws_credentials_json.get('name')

        r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
        aws_credential_details = r.json()
        print(aws_credential_details)

        connection_status = aws_credential_details.get('connectionStatus')
        label = aws_credential_details.get('label')
        partition_type = aws_credential_details.get('partitionType')
        authentication_data = aws_credential_details.get('authenticationData')
        authentication_type = authentication_data.get('type')
        tagged_only = aws_credential_details.get('taggedOnly')
        tags_to_monitor = aws_credential_details.get('tagsToMonitor')
        supporting_services_to_monitor = aws_credential_details.get('supportingServicesToMonitor')
        supporting_service_list = []
        for supporting_service in supporting_services_to_monitor:
            name = supporting_service.get('name')
            supporting_service_list.append(name)

        if not summary_mode:
            rows.append((name, entity_id, connection_status, label, partition_type, authentication_type, tagged_only, str(tags_to_monitor), str(supporting_service_list)))

        count_total += 1

    summary.append('There are ' + str(count_total) + ' AWS accounts currently configured.')

    if not summary_mode:
        report_name = 'AWS Credentials'
        report_writer.initialize_text_file(None)
        report_headers = ('Name', 'ID', 'Connection Status', 'Label', 'Partition Type', 'Authentication Type', 'Tagged Only', 'Tags To Monitor', 'Supporting Services')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total AWS Accounts: ' + str(count_total)])
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
