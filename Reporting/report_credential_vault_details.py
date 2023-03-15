from Reuse import dynatrace_api
from Reuse import environment

friendly_type_name = {'CERTIFICATE': 'certificate', 'TOKEN': 'token', 'USERNAME_PASSWORD': 'username/password'}


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    if print_mode:
        print('name' + '|' + 'id' + '|' + 'type' + '|' + 'description' + '|' + 'owner' + '|' + 'ownerAccessOnly' + '|' + 'scope' + '|' + 'externalVault' + '|' + 'credentialUsageSummary')

    summary.append(process_type(env, token, print_mode, 'CERTIFICATE')[0])
    summary.append(process_type(env, token, print_mode, 'TOKEN')[0])
    summary.append(process_type(env, token, print_mode, 'USERNAME_PASSWORD')[0])

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def process_type(env, token, print_mode, entity_type):
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

            if print_mode:
                print(name + '|' + entity_id + '|' + entity_type + '|' + description + '|' + owner + '|' + str(owner_access_only) + '|' + scope + '|' + str(external_vault) + '|' + credential_usage_summary_str)

            count_total += 1

    if print_mode:
        print('Total Credential Vault Entries - ' + friendly_type_name[entity_type] + ': ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' credential value entries of the ' + friendly_type_name[entity_type] + ' type currently defined.')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)
        

def main():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
