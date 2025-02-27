import json

from Reuse import environment
from Reuse import new_platform_api
from Reuse import report_writer


def process(env, client_id, client_secret):
    scope = 'app-engine:apps:run'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/app-engine/registry/v1/apps', params)
    applications_json = json.loads(results.text)
    application_list = applications_json.get('apps')
    # print(applications_json)
    headers = [['Name', 'ID', 'Version', 'Description', 'Resource Status', 'App Icon', 'Signed', 'Publisher', 'Created By', 'Last Modified By', 'Last Modified At']]
    rows = []
    for application in application_list:
        application_id = application.get('id')
        application_name = application.get('name')
        application_version = application.get('version')
        application_description = application.get('description')
        application_resourceStatus = application.get('resourceStatus').get('status')
        application_appIcon = application.get('appIcon').get('href')
        application_signatureInfo_signed = application.get('signatureInfo').get('signed')
        application_signatureInfo_publisher = application.get('signatureInfo').get('publisher')
        application_modificationInfo = application.get('modificationInfo')
        application_modificationInfo_createdBy = application_modificationInfo.get('createdBy')
        application_modificationInfo_lastModifiedBy = application_modificationInfo.get('lastModifiedBy')
        application_modificationInfo_lastModifiedAt = application_modificationInfo.get('lastModifiedAt')
        rows.append([application_name, application_id, application_version, application_description, application_resourceStatus, application_appIcon, application_signatureInfo_signed, application_signatureInfo_publisher, application_modificationInfo_createdBy, application_modificationInfo_lastModifiedBy, application_modificationInfo_lastModifiedAt])

    """
    {'apps': [{'id': 'dynatrace.appshell', 'name': 'App Shell', 'version': '1.1302.2', 'description': 'Hosts your apps', 'resourceStatus': {'status': 'OK'}, 'appIcon': {'href': '/platform/app-engine/registry/v1/app-icons/dynatrace.appshell?appVersion=1.1302.2'}, 'signatureInfo': {'signed': True, 'publisher': 'Dynatrace'}, 'modificationInfo': {'createdBy': 'system', 'createdAt': '2024-12-12T08:52:04.912Z', 'lastModifiedBy': 'system', 'lastModifiedAt': '2025-02-19T13:43:45.769Z'}}
    """

    report_writer.print_rows(headers, sorted(rows))


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Sandbox'
    #
    # env_name_supplied = 'Upper'
    # env_name_supplied = 'Lower'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, client_id, client_secret)


if __name__ == '__main__':
    main()
