import json

from Reuse import environment
from Reuse import new_platform_api
from Reuse import report_writer


def process(env, client_id, client_secret):
    scope = 'document:direct-shares:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/direct-shares', params)
    direct_shares_json = json.loads(results.text)
    direct_share_list = direct_shares_json.get('direct-shares')
    headers = [['Environment Share ID', 'Document ID', 'Access', 'Claims']]
    rows = []
    for direct_share in direct_share_list:
        # print(direct_share)
        # exit(9999)
        direct_share_id = direct_share.get('id')
        direct_share_document_id = direct_share.get('documentId')
        direct_share_access = direct_share.get('access')
        direct_share_claim_count = direct_share.get('claimCount')
        rows.append([direct_share_id, direct_share_document_id, report_writer.stringify_list(direct_share_access), direct_share_claim_count])

    report_writer.print_rows(headers, sorted(rows))


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    env_name_supplied = 'NonProd'
    # env_name_supplied = 'Int'
    # env_name_supplied = 'Personal'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, client_id, client_secret)


if __name__ == '__main__':
    main()
