from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

friendly_type_name = {'CERTIFICATE': 'certificate', 'TOKEN': 'token', 'USERNAME_PASSWORD': 'username/password'}


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []
    count_total = 0

    type_rows, type_summary, type_count = process_type(env, token, summary_mode, 'CERTIFICATE')
    rows.extend(type_rows)
    summary.extend(type_summary)
    count_total += type_count
    type_rows, type_summary, type_count = process_type(env, token, summary_mode, 'TOKEN')
    rows.extend(type_rows)
    summary.extend(type_summary)
    count_total += type_count
    type_rows, type_summary, type_count = process_type(env, token, summary_mode, 'USERNAME_PASSWORD')
    rows.extend(type_rows)
    summary.extend(type_summary)
    count_total += type_count

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Credential Vault Entries'
        report_writer.initialize_text_file(None)
        report_headers = ('name', 'id', 'type', 'description', 'owner', 'ownerAccessOnly', 'scope', 'externalVault', 'credentialUsageSummary')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Credential Vault Entries: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def process_type(env, token, summary_mode, entity_type):
    rows = []
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/credentials'
    params = 'type=' + entity_type
    credential_vault_json_list = dynatrace_api.get(env, token, endpoint, params)

    for credential_vault_json in credential_vault_json_list:
        inner_credential_vault_json_list = credential_vault_json.get('credentials')
        for inner_credential_vault_json in inner_credential_vault_json_list:
            name = inner_credential_vault_json.get('name')
            entity_id = inner_credential_vault_json.get('id')
            entity_type = inner_credential_vault_json.get('type')
            description = inner_credential_vault_json.get('description')
            owner = inner_credential_vault_json.get('owner')
            owner_access_only = inner_credential_vault_json.get('ownerAccessOnly')
            scope = inner_credential_vault_json.get('scope')
            external_vault = inner_credential_vault_json.get('externalVault')
            credential_usage_summary = inner_credential_vault_json.get('credentialUsageSummary')

            credential_usage_summary_str = str(credential_usage_summary).replace('[', '')
            credential_usage_summary_str = credential_usage_summary_str.replace(']', '')
            credential_usage_summary_str = credential_usage_summary_str.replace('{', '')
            credential_usage_summary_str = credential_usage_summary_str.replace('}', '')
            credential_usage_summary_str = credential_usage_summary_str.replace("'type': '", "")
            credential_usage_summary_str = credential_usage_summary_str.replace("', 'count'", "")

            if not summary_mode:
                rows.append((name, entity_id, entity_type, description, owner, str(owner_access_only), scope, str(external_vault), credential_usage_summary_str))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' credential value entries of the ' + friendly_type_name[entity_type] + ' type currently defined.')

    return rows, summary, count_total


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
