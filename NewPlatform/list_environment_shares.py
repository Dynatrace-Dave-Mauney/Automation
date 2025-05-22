import json

from Reuse import environment
from Reuse import new_platform_api
from Reuse import report_writer


def process(env, client_id, client_secret):
    scope = 'document:environment-shares:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/environment-shares', params)
    environment_shares_json = json.loads(results.text)
    environment_share_list = environment_shares_json.get('environment-shares')
    headers = [['Environment Share ID', 'Document ID', 'Access', 'Claims']]
    rows = []
    for environment_share in environment_share_list:
        environment_share_id = environment_share.get('id')
        environment_share_document_id = environment_share.get('documentId')
        environment_share_access = environment_share.get('access')
        environment_share_claim_count = environment_share.get('claimCount')
        rows.append([environment_share_id, environment_share_document_id, report_writer.stringify_list(environment_share_access), environment_share_claim_count])

    report_writer.print_rows(headers, sorted(rows))


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, client_id, client_secret)


if __name__ == '__main__':
    main()
