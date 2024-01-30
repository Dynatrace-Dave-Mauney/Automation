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

    endpoint = '/api/config/v1/azure/credentials'
    azure_credentials_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for azure_credentials_json in azure_credentials_json_list:
        inner_azure_credentials_json_list = azure_credentials_json.get('values')
        for inner_azure_credentials_json in inner_azure_credentials_json_list:
            entity_id = inner_azure_credentials_json.get('id')
            name = inner_azure_credentials_json.get('name')

            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            azure_credentials = r.json()
            # print(azure_credentials)
            label = azure_credentials.get('label')
            app_id = azure_credentials.get('appId')
            directory_id = azure_credentials.get('directoryId')
            key = azure_credentials.get('key')
            active = azure_credentials.get('active')
            auto_tagging = azure_credentials.get('autoTagging')
            monitor_only_tagged_entities = azure_credentials.get('monitorOnlyTaggedEntities')
            monitor_only_tag_pairs = azure_credentials.get('monitorOnlyTagPairs')
            monitor_only_excluding_tag_pairs = azure_credentials.get('monitorOnlyExcludingTagPairs')
            supporting_services = azure_credentials.get('supportingServices')
            supporting_service_names = []
            for supporting_service in supporting_services:
                supporting_service_name = supporting_service.get('name')
                supporting_service_names.append(supporting_service_name)

            if not summary_mode:
                rows.append((name, label, entity_id, app_id, directory_id, key, active, auto_tagging, monitor_only_tagged_entities, str(monitor_only_tag_pairs), str(monitor_only_excluding_tag_pairs), str(supporting_service_names)))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' azure subscriptions currently configured.')

    if not summary_mode:
        report_name = 'Azure Subscriptions'
        report_writer.initialize_text_file(None)
        report_headers = ('Name', 'label', 'ID', 'appId', 'directoryId', 'key', 'active', 'autoTagging', 'monitorOnlyTaggedEntities', 'monitorOnlyTagPairs', 'monitorOnlyExcludingTagPairs', 'supportingServices')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Azure Subscriptions: ' + str(count_total)])
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
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
